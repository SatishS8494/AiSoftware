from state import ProjectState

def has_pending_files(
    state: ProjectState
) -> str:

    if state.pending_files:
        return "queue"

    return "end"

def fix_router(
    state: ProjectState
):

    if state.bug_report.success:
        return "completed"

    if state.fix_attempts >= state.max_fix_attempts:
        return "failed"

    return "fixer"