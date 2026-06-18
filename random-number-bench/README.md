# Random Number Bench

A benchmark that measures whether large language models can produce genuinely
random output. Each model is asked to pick a random number between 1 and 10, one
hundred times. A model drawing uniformly at random scores about 10/100; the
benchmark surfaces how far each model deviates from that baseline and which
numbers it favors.

Random Number Bench is a research project of the
**[Columbus Technology Institute](https://github.com/henrygmarkwardt/columbus-technology-institute)**.
The full write-up lives on the Institute's website as the page
`random-number-bench.html` (in the
[columbus-technology-institute](https://github.com/henrygmarkwardt/columbus-technology-institute)
repository).

This project lives in the Columbus Technology Institute website repository at
[`/random-number-bench`](https://github.com/henrygmarkwardt/columbus-technology-institute/tree/main/random-number-bench).
The interactive leaderboard is in this folder's `docs/` directory.

## How it works

Each trial:

1. We pick a number 1–10 uniformly at random, before calling the model.
2. We send the model the prompt: *"Pick a random number between 1 and 10. Reply
   with just the number, nothing else."*
3. We parse the first valid 1–10 integer from the model's reply and compare it to
   our number.

A model's score is the number of matches out of 100 trials. A uniformly random
model is expected to score about 10/100. The benchmark also records the full
distribution of the model's picks across the ten numbers, which exposes systematic
biases (most models heavily favor 7).

Trials run concurrently. Transport errors (HTTP 429 and transient 5xx/network
failures) are retried with exponential backoff that respects `Retry-After` and
`X-RateLimit-Reset` headers; `:free` models are automatically capped to lower
concurrency to stay within their shared rate limit. A successful response whose
body is empty or unparseable is re-requested up to a fixed cap so every recorded
trial is a genuine, scorable answer.

## Setup

**Requirements:** Python 3.11+, an [OpenRouter](https://openrouter.ai) API key.

```bash
git clone https://github.com/henrygmarkwardt/columbus-technology-institute
cd columbus-technology-institute/random-number-bench
pip install -e .
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

## Run the benchmark

```bash
python -m benchmark run --model qwen/qwen3.7-plus
```

Replace `qwen/qwen3.7-plus` with any [OpenRouter model ID](https://openrouter.ai/models).
Results are appended to `docs/results.json`.

Optional flags:

- `--concurrency N` — number of concurrent API requests (default 10; `:free`
  models are capped to 4 automatically).

## Current results

Eleven models have been benchmarked so far. Scores out of 100 (a uniformly random
model is expected to score ~10):

| Model | Score / 100 |
|-------|-------------|
| `x-ai/grok-build-0.1` | 12 |
| `google/gemini-3.1-flash-lite` | 12 |
| `anthropic/claude-haiku-4.5` | 12 |
| `minimax/minimax-m3` | 11 |
| `z-ai/glm-5.2` | 10 |
| `xiaomi/mimo-v2.5-pro` | 9 |
| `moonshotai/kimi-k2.7-code` | 9 |
| `qwen/qwen3.7-plus` | 8 |
| `ibm-granite/granite-4.1-8b` | 8 |
| `mistralai/mistral-medium-3-5` | 6 |
| `nex-agi/nex-n2-pro:free` | 5 |

Across all eleven models and 1,100 total guesses, the number 7 was chosen 1,076
times — the dominant bias the benchmark is designed to reveal.

## Contributing results

1. Fork this repository.
2. Set up as above.
3. Run the benchmark against a model not yet in `docs/results.json`.
4. Commit the updated `docs/results.json`.
5. Open a pull request.

## Run tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```
