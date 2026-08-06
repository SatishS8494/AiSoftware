from llm import llm 
from state import ProjectState 
from prompts import ARCHITECT_PROMPT 
from models import ProjectManifest 
from agents.base_agent import BaseAgent

class ArchitectAgent(BaseAgent):
    def __init__(self,llm): 
        super().__init__( 
            llm.with_structured_output( 
                ProjectManifest 
            ) 
        ) 

    def run( self, state: ProjectState ) -> ProjectState: 
        prompt = f""" 
    {ARCHITECT_PROMPT} 
    Project Plan {state.plan.model_dump_json(indent=2)} """ 
        manifest = self.llm.invoke( prompt ) 
        state.manifest = manifest 
        return state