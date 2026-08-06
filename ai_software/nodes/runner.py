from pathlib import Path

from state import ProjectState
from tools.python_runner import PythonRunner


runner = PythonRunner()


def runner_node(
    state: ProjectState
):

    project_path = Path("workspace")

    state.execution_result = runner.run(
        project_path
    )

    return state