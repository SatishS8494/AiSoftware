from pathlib import Path

from state import ProjectState
from tools.language_runner import run_project


def runner_node(
    state: ProjectState
):

    project_path = Path("workspace")
    language = state.plan.language if state.plan else "python"

    state.execution_result = run_project(project_path, language)

    return state