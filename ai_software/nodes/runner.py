from pathlib import Path

from config import settings
from state import ProjectState
from tools.language_runner import run_project


def runner_node(
    state: ProjectState
):

    project_path = Path(settings.workspace_path)
    language = state.plan.language if state.plan else "python"

    state.execution_result = run_project(project_path, language)

    return state