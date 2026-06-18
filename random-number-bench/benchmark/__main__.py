import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from benchmark.runner import run_benchmark
from benchmark.results import save_result

RESULTS_PATH = Path(__file__).parent.parent / "docs" / "results.json"


def cmd_run(args):
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set. Copy .env.example to .env and add your key.")
        raise SystemExit(1)

    print(f"Running benchmark: {args.model} — 100 trials (concurrency {args.concurrency})...")
    result = run_benchmark(args.model, api_key, concurrency=args.concurrency)

    save_result(RESULTS_PATH, result)

    print(f"\nResults for {result['model']} ({result['date']})")
    print(f"  Score:    {result['score']}/100")
    print(f"  Invalid:  {result['invalid']}")
    print(f"  Distribution: {result['distribution']}")
    print(f"\nSaved to {RESULTS_PATH}")


def main():
    parser = argparse.ArgumentParser(prog="benchmark")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Run benchmark against a model")
    run_parser.add_argument("--model", required=True, help="OpenRouter model ID, e.g. qwen/qwen3-7-plus")
    run_parser.add_argument("--concurrency", type=int, default=10,
                            help="Number of concurrent API requests (default 10)")
    run_parser.set_defaults(func=cmd_run)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
