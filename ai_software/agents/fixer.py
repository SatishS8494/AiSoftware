from llm import llm 
from prompts import FIX_PROMPT 
from state import ProjectState 
from base_agent import BaseAgent

class FixAgent(BaseAgent): 
    def __init__(self, llm): 
        super().__init__(llm)
        
    def run( self, state: ProjectState ) -> ProjectState: 
        state.fix_attempts += 1
        generated_file = state.generated_files[-1] 
        prompt = FIX_PROMPT.format( 
            file_path=generated_file.path, 
            source_code=generated_file.content, 
            execution=state.execution_result.model_dump_json(indent=2),
            bug_report=state.bug_report.model_dump_json(indent=2) ) 
        response = llm.invoke(prompt) 
        generated_file.content = response.content 
        return state