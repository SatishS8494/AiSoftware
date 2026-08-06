from state import ProjectState 

def initialize_queue( state: ProjectState ): 
    state.pending_files = list( state.manifest.files ) 
    return state