# Entry point: picks a workflow by name and runs it, so one harness can drive many workflows.
import argparse

from workflows import WORKFLOWS  # every workflow by name, from workflows/__init__.py


def main():
    parser = argparse.ArgumentParser(description="Run an Incident-Trawlers workflow.")
    parser.add_argument("workflow", nargs="?", default="default", choices=WORKFLOWS)
    parser.add_argument("--prompt", help="override the workflow's default prompt")
    args = parser.parse_args()

    workflow = WORKFLOWS[args.workflow]  # picks the state, tools and prompt to use
    result = workflow.run(args.prompt)  # builds the core graph and runs it to END

    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
