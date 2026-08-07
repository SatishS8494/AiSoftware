import argparse
import uuid

from graph import graph
from state import ProjectState


SEP = "=" * 60


def _parse_args():
    parser = argparse.ArgumentParser(description="AI Software Company")
    parser.add_argument(
        "--thread",
        default=None,
        help="Thread ID to resume an existing checkpointed run. Omit to start a new one.",
    )
    return parser.parse_args()


def _section(title: str) -> None:
    print(f"\n{SEP}\n{title}\n{SEP}")


def _print_files(result) -> None:
    files = result.get("generated_files") or []
    _section(f"Generated Files ({len(files)})")
    for f in files:
        print(f.path)


def _print_execution(result) -> None:
    execution = result.get("execution_result")
    if not execution:
        return
    _section("Execution Result")
    print(f"Success     : {execution.success}")
    print(f"Return Code : {execution.return_code}")
    if execution.stdout:
        print(f"\nSTDOUT\n{execution.stdout}")
    if execution.stderr:
        print(f"\nSTDERR\n{execution.stderr}")


def _print_bug_report(result) -> None:
    report = result.get("bug_report")
    if not report:
        return
    _section("Bug Report")
    print(f"Success        : {report.success}")
    print(f"Summary        : {report.summary}")
    print(f"Cause          : {report.probable_cause}")
    print(f"Recommendation : {report.recommendation}")


def _print_review(result) -> None:
    review = result.get("review_report")
    if not review:
        return
    _section("Review Report")
    print(f"Approved  : {review.approved}")
    print(f"Score     : {review.score}")
    print(f"Summary   : {review.summary}")
    if review.strengths:
        print("Strengths:")
        for s in review.strengths:
            print(f"  - {s}")
    if review.improvements:
        print("Improvements:")
        for i in review.improvements:
            print(f"  - {i}")


def main():
    args = _parse_args()
    thread_id = args.thread or str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"Thread ID: {thread_id}  (pass --thread {thread_id} to resume)")

    if args.thread:
        result = graph.invoke(None, config=config)
    else:
        requirement = input("Requirement:\n")
        state = ProjectState(requirement=requirement)
        result = graph.invoke(state, config=config)

    _print_files(result)
    _print_execution(result)
    _print_bug_report(result)
    _print_review(result)


if __name__ == "__main__":
    main()
