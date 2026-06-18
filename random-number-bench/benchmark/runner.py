import random
import re
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import date

import requests


def parse_response(text: str) -> int | None:
    """Return first digit 1-10 found in text, or None."""
    matches = re.findall(r'\b(10|[1-9])\b', text)
    if not matches:
        return None
    return int(matches[0])


PROMPT = "Pick a random number between 1 and 10. Reply with just the number, nothing else."
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

MAX_RETRIES = 6
BACKOFF_BASE = 1.0

# Content-level re-roll cap. A successful HTTP response whose body is malformed,
# empty, or unparseable yields no valid 1-10 answer; we re-request the model
# until it does. A model could (pathologically) never return a parseable answer,
# so we bound the re-rolls. Exhausting this cap is a genuine failure for that
# trial and raises, rather than silently recording an invalid result, because the
# benchmark's contract is 100 good, scorable results per model.
MAX_VALID_ATTEMPTS = 12

# OpenRouter caps :free models at a low shared rate (~16-20 requests/min). Running
# many concurrent requests against one free model blows past that limit and every
# retry hammers the same low ceiling, so we cap concurrency for :free models.
FREE_MODEL_CONCURRENCY = 4


def _retry_delay(response: requests.Response, attempt: int) -> float:
    """How long to wait before retrying a rate-limited / 5xx response.

    Respects Retry-After and X-RateLimit-Reset headers when present, otherwise
    falls back to exponential backoff. A little jitter avoids a thundering herd
    of concurrent retries all firing at the same instant.
    """
    delay = None
    retry_after = response.headers.get("Retry-After")
    if retry_after is not None:
        try:
            delay = float(retry_after)
        except ValueError:
            delay = None
    if delay is None:
        reset = response.headers.get("X-RateLimit-Reset")
        if reset is not None:
            try:
                # OpenRouter sends this as a unix timestamp in milliseconds.
                delay = max(0.0, float(reset) / 1000.0 - time.time())
            except ValueError:
                delay = None
    if delay is None:
        delay = BACKOFF_BASE * (2 ** attempt)
    return delay + random.random()


def _post_with_retry(model: str, api_key: str) -> requests.Response:
    """POST to OpenRouter, retrying on 429 and transient 5xx/network errors.

    Uses exponential backoff with jitter and respects the Retry-After /
    X-RateLimit-Reset headers when present. Client errors other than 429
    (e.g. bad model ID -> 400/404) fail fast.
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": PROMPT}],
                },
                timeout=30,
            )
        except requests.exceptions.RequestException:
            # Transient network error: retry unless we're out of attempts.
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(BACKOFF_BASE * (2 ** attempt))
            continue

        if response.status_code == 429 or response.status_code >= 500:
            if attempt == MAX_RETRIES - 1:
                response.raise_for_status()
                return response
            time.sleep(_retry_delay(response, attempt))
            continue

        response.raise_for_status()
        return response

    # Unreachable: loop either returns or raises.
    raise RuntimeError("retry loop exhausted")


def _extract_content(response: requests.Response) -> str | None:
    """Pull the assistant message text out of an OpenRouter response body.

    Returns the content string, or None if the body is malformed/empty in a
    way we want to treat as an *invalid* trial rather than a hard error:
      - no/empty ``choices`` (provider returned an error-shaped 200 body),
      - missing ``message``/``content`` keys,
      - ``content`` is null (common with reasoning/code models).
    We only swallow these specific shape problems; anything else propagates.
    """
    body = response.json()
    if not isinstance(body, dict):
        return None
    choices = body.get("choices")
    if not choices:
        return None
    content = choices[0].get("message", {}).get("content")
    if content is None:
        return None
    return content


def run_trial(model: str, api_key: str) -> dict:
    """Run one trial: pick our number, query model (re-rolling until valid), compare.

    ``our_number`` is picked exactly once for the trial. We then request the
    model's answer; if the HTTP call succeeded but the body is malformed/empty/
    unparseable (no valid 1-10 int), we re-request the model's answer ONLY, up to
    ``MAX_VALID_ATTEMPTS`` times, keeping ``our_number`` fixed so the match isn't
    biased. This content-level re-roll is distinct from ``_post_with_retry``,
    which handles transport/HTTP-status retries (429/5xx/network) on each request.

    Raises ``RuntimeError`` if every attempt yields an unparseable answer: the
    benchmark requires 100 good results, so a never-parseable trial surfaces as a
    real failure rather than a silently-recorded invalid.
    """
    # SystemRandom is thread-safe, unlike the shared module-level random instance.
    our_number = random.SystemRandom().randint(1, 10)

    for _ in range(MAX_VALID_ATTEMPTS):
        # Transport/HTTP errors (bad model id -> 4xx, transient 5xx/429) are raised
        # by _post_with_retry and intentionally propagate. A *successful* HTTP
        # response with a malformed/empty body just triggers a content re-roll.
        response = _post_with_retry(model, api_key)

        content = _extract_content(response)
        model_number = parse_response(content.strip()) if content is not None else None

        if model_number is not None:
            return {
                "our_number": our_number,
                "model_number": model_number,
                "correct": model_number == our_number,
                "invalid": False,
            }

    raise RuntimeError(
        f"{model}: no valid 1-10 answer after {MAX_VALID_ATTEMPTS} attempts"
    )


def run_benchmark(model: str, api_key: str, runs: int = 100, concurrency: int = 10) -> dict:
    """Run the full benchmark concurrently and return a result record."""
    # :free models share a low (~16-20 req/min) rate limit, so high concurrency
    # just triggers sustained 429s. Cap it for them without slowing paid models.
    if model.endswith(":free"):
        concurrency = min(concurrency, FREE_MODEL_CONCURRENCY)

    # Run trials concurrently; threads parallelize the blocking network waits.
    # Each future returns an independent trial dict with no shared mutable state.
    #
    # We deliberately do NOT swallow per-trial exceptions here. The contract is
    # 100 good, scorable results, so a trial that exhausts its content re-rolls
    # (RuntimeError from run_trial) or its transport retries (HTTPError from
    # _post_with_retry) is a real failure and propagates out of executor.map,
    # rather than being silently degraded to an invalid result.
    def _trial(_):
        return run_trial(model, api_key)

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        trials = list(executor.map(_trial, range(runs)))

    # Single-threaded tally pass: lock-free accumulation.
    distribution = defaultdict(int)
    score = 0
    invalid_count = 0

    for trial in trials:
        if trial["invalid"]:
            invalid_count += 1
        else:
            distribution[str(trial["model_number"])] += 1
            if trial["correct"]:
                score += 1

    full_distribution = {str(n): distribution[str(n)] for n in range(1, 11)}

    return {
        "model": model,
        "date": date.today().isoformat(),
        "score": score,
        "runs": runs,
        "distribution": full_distribution,
        "invalid": invalid_count,
    }
