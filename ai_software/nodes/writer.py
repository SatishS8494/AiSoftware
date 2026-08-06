from state import ProjectState 
from tools.file_writer import FileWriter 

writer = FileWriter() 

def writer_node( state: ProjectState ): 
    if not state.generated_files: return state 
    latest_file = state.generated_files[-1]
    writer.write( latest_file ) 
    return state