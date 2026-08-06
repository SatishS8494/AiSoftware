from state import ProjectState


def retry_node(
    state: ProjectState
) -> ProjectState:

    if state.retry_count < state.max_retries:

        state.pending_files.insert(
            0,
            state.current_file
        )

        state.retry_count += 1

    return state