import json
import pytest
from pathlib import Path
from benchmark.results import load_results, save_result


@pytest.fixture
def results_file(tmp_path):
    path = tmp_path / "results.json"
    path.write_text("[]")
    return path


def test_load_results_empty(results_file):
    assert load_results(results_file) == []


def test_load_results_existing(results_file):
    existing = [{"model": "test/model", "score": 10}]
    results_file.write_text(json.dumps(existing))
    assert load_results(results_file) == existing


def test_save_result_appends(results_file):
    record = {"model": "test/model", "date": "2026-06-16", "score": 10,
              "runs": 100, "distribution": {str(i): 10 for i in range(1, 11)}, "invalid": 0}
    save_result(results_file, record)
    data = json.loads(results_file.read_text())
    assert len(data) == 1
    assert data[0]["model"] == "test/model"


def test_save_result_preserves_existing(results_file):
    first = {"model": "a/model", "score": 9}
    results_file.write_text(json.dumps([first]))
    second = {"model": "b/model", "score": 11}
    save_result(results_file, second)
    data = json.loads(results_file.read_text())
    assert len(data) == 2
    assert data[0]["model"] == "a/model"
    assert data[1]["model"] == "b/model"
