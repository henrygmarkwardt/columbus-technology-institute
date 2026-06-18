import pytest
from benchmark.runner import parse_response


def test_parse_plain_digit():
    assert parse_response("7") == 7

def test_parse_digit_in_sentence():
    assert parse_response("The number is 7.") == 7

def test_parse_first_digit_wins():
    assert parse_response("I pick 3, or maybe 8.") == 3

def test_parse_10():
    assert parse_response("10") == 10

def test_parse_zero_is_invalid():
    assert parse_response("0") is None

def test_parse_11_is_invalid():
    assert parse_response("11") is None

def test_parse_word_form_is_invalid():
    assert parse_response("seven") is None

def test_parse_empty_is_invalid():
    assert parse_response("") is None

def test_parse_whitespace_only_is_invalid():
    assert parse_response("   ") is None


from unittest.mock import patch, MagicMock
from benchmark.runner import run_trial


def test_run_trial_correct():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "5"}}]
    }
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch("benchmark.runner.requests.post", return_value=mock_response):
        with patch("benchmark.runner.random.SystemRandom.randint", return_value=5):
            trial = run_trial("qwen/qwen3-7-plus", "test-key")

    assert trial["our_number"] == 5
    assert trial["model_number"] == 5
    assert trial["correct"] is True
    assert trial["invalid"] is False


def test_run_trial_incorrect():
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "3"}}]
    }
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()

    with patch("benchmark.runner.requests.post", return_value=mock_response):
        with patch("benchmark.runner.random.SystemRandom.randint", return_value=7):
            trial = run_trial("qwen/qwen3-7-plus", "test-key")

    assert trial["our_number"] == 7
    assert trial["model_number"] == 3
    assert trial["correct"] is False
    assert trial["invalid"] is False


def test_run_trial_invalid_then_valid_rerolls():
    # First response is unparseable junk; the re-roll then returns a valid answer.
    # The trial must return the valid result (never invalid) after re-requesting.
    junk = _mock_ok_response({"choices": [{"message": {"content": "I don't know"}}]})
    good = _mock_ok_response({"choices": [{"message": {"content": "4"}}]})

    with patch("benchmark.runner.requests.post", side_effect=[junk, good]) as mock_post:
        with patch("benchmark.runner.random.SystemRandom.randint", return_value=4) as mock_rand:
            trial = run_trial("qwen/qwen3-7-plus", "test-key")

    assert trial["our_number"] == 4
    assert trial["model_number"] == 4
    assert trial["correct"] is True
    assert trial["invalid"] is False
    assert mock_post.call_count == 2  # re-requested once after the junk answer
    assert mock_rand.call_count == 1  # our_number picked exactly once for the trial


def _mock_ok_response(body):
    mock_response = MagicMock()
    mock_response.json.return_value = body
    mock_response.status_code = 200
    mock_response.raise_for_status = MagicMock()
    return mock_response


# Each of these malformed-body shapes (no 'choices', empty 'choices', null
# content, empty content string, missing 'message' key) yields no valid 1-10
# answer and must trigger a content-level re-roll rather than an invalid trial.
# Here the re-roll eventually returns a valid answer, so the trial succeeds.
import pytest as _pytest


@_pytest.mark.parametrize("bad_body", [
    {"error": {"message": "provider error"}},      # no 'choices'
    {"choices": []},                                # empty 'choices'
    {"choices": [{"message": {"content": None}}]},  # null content
    {"choices": [{"message": {"content": ""}}]},    # empty content string
    {"choices": [{}]},                              # missing 'message' key
])
def test_run_trial_malformed_body_rerolls_to_valid(bad_body):
    bad = _mock_ok_response(bad_body)
    good = _mock_ok_response({"choices": [{"message": {"content": "4"}}]})

    with patch("benchmark.runner.requests.post", side_effect=[bad, good]) as mock_post:
        with patch("benchmark.runner.random.SystemRandom.randint", return_value=4) as mock_rand:
            trial = run_trial("z-ai/glm-5.2", "test-key")

    assert trial["model_number"] == 4
    assert trial["invalid"] is False
    assert trial["correct"] is True
    assert mock_post.call_count == 2  # re-rolled once after the malformed body
    assert mock_rand.call_count == 1  # our_number fixed across the re-roll


def test_run_trial_raises_when_never_parseable():
    # If every attempt up to MAX_VALID_ATTEMPTS is unparseable, the trial raises
    # rather than recording an invalid result (the contract is 100 good results).
    junk = _mock_ok_response({"choices": [{"message": {"content": "nope"}}]})

    with patch("benchmark.runner.requests.post", return_value=junk) as mock_post:
        with patch("benchmark.runner.random.SystemRandom.randint", return_value=4):
            with _pytest.raises(RuntimeError):
                run_trial("moonshotai/kimi-k2.7-code", "test-key")

    assert mock_post.call_count == MAX_VALID_ATTEMPTS  # exhausted the cap


from benchmark.runner import (
    run_benchmark,
    _post_with_retry,
    FREE_MODEL_CONCURRENCY,
    MAX_VALID_ATTEMPTS,
)
import requests


def test_post_with_retry_raises_after_sustained_429():
    # Failure 4: a 429 that never clears exhausts retries and raises (HTTPError).
    rate_limited = MagicMock()
    rate_limited.status_code = 429
    rate_limited.headers = {}
    rate_limited.raise_for_status.side_effect = requests.exceptions.HTTPError("429")

    with patch("benchmark.runner.requests.post", return_value=rate_limited):
        with patch("benchmark.runner.time.sleep"):
            with pytest.raises(requests.exceptions.HTTPError):
                _post_with_retry("nvidia/nemotron:free", "test-key")


def test_run_benchmark_propagates_trial_exception():
    # A trial that raises (exhausted content re-rolls -> RuntimeError, or
    # exhausted transport retries -> HTTPError) is a real failure: the contract
    # is 100 good results, so it surfaces rather than being degraded to invalid.
    def boom(*args, **kwargs):
        raise requests.exceptions.HTTPError("429")

    with patch("benchmark.runner.run_trial", side_effect=boom):
        with pytest.raises(requests.exceptions.HTTPError):
            run_benchmark("nvidia/nemotron:free", "test-key", runs=5, concurrency=2)


def test_run_benchmark_caps_free_model_concurrency():
    captured = {}
    real_executor = run_benchmark.__globals__["ThreadPoolExecutor"]

    def spy_executor(max_workers):
        captured["max_workers"] = max_workers
        return real_executor(max_workers=max_workers)

    fake_trials = [
        {"our_number": 1, "model_number": 1, "correct": True, "invalid": False}
        for _ in range(10)
    ]
    with patch("benchmark.runner.ThreadPoolExecutor", side_effect=spy_executor):
        with patch("benchmark.runner.run_trial", side_effect=fake_trials):
            run_benchmark("nvidia/nemotron:free", "test-key", runs=10, concurrency=10)

    assert captured["max_workers"] == FREE_MODEL_CONCURRENCY


def test_post_with_retry_retries_on_429_then_succeeds():
    rate_limited = MagicMock()
    rate_limited.status_code = 429
    rate_limited.headers = {}
    ok = MagicMock()
    ok.status_code = 200
    ok.raise_for_status = MagicMock()

    with patch("benchmark.runner.requests.post", side_effect=[rate_limited, ok]):
        with patch("benchmark.runner.time.sleep") as mock_sleep:
            response = _post_with_retry("qwen/qwen3-7-plus", "test-key")

    assert response is ok
    mock_sleep.assert_called_once()  # backed off once before the retry


def test_post_with_retry_fails_fast_on_404():
    not_found = MagicMock()
    not_found.status_code = 404
    not_found.raise_for_status.side_effect = requests.exceptions.HTTPError("404")

    with patch("benchmark.runner.requests.post", return_value=not_found) as mock_post:
        with pytest.raises(requests.exceptions.HTTPError):
            _post_with_retry("bad/model", "test-key")

    assert mock_post.call_count == 1  # no retries on a client error


def test_run_benchmark_structure():
    # Every trial is now a valid result (run_trial re-rolls until valid), so
    # invalid is 0 and all 100 runs land in the distribution.
    fake_trials = [
        {"our_number": i % 10 + 1, "model_number": (i % 10) + 1, "correct": (i % 10) != 0, "invalid": False}
        for i in range(100)
    ]

    with patch("benchmark.runner.run_trial", side_effect=fake_trials):
        result = run_benchmark("qwen/qwen3-7-plus", "test-key")

    assert result["model"] == "qwen/qwen3-7-plus"
    assert result["runs"] == 100
    assert result["score"] == 90  # 10 of the 100 trials have correct=False
    assert result["invalid"] == 0
    assert isinstance(result["date"], str)
    assert set(result["distribution"].keys()) == {str(i) for i in range(1, 11)}
    assert sum(result["distribution"].values()) == 100  # all 100 runs are valid


def test_run_benchmark_concurrent_aggregate_matches():
    # Every trial correct, picking number = (index % 10) + 1.
    fake_trials = [
        {"our_number": (i % 10) + 1, "model_number": (i % 10) + 1, "correct": True, "invalid": False}
        for i in range(100)
    ]

    with patch("benchmark.runner.run_trial", side_effect=fake_trials):
        result = run_benchmark("qwen/qwen3-7-plus", "test-key", concurrency=8)

    assert set(result.keys()) == {"model", "date", "score", "runs", "distribution", "invalid"}
    assert result["runs"] == 100
    assert result["score"] == 100
    assert result["invalid"] == 0
    assert set(result["distribution"].keys()) == {str(i) for i in range(1, 11)}
    assert sum(result["distribution"].values()) == 100
    # Each of the 10 numbers should have been picked exactly 10 times.
    assert all(v == 10 for v in result["distribution"].values())
