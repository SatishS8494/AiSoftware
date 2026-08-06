from llm import llm 
from prompts import PLANNER_PROMPT 
from state import ProjectState 
from models import ProjectPlan
from agents.base_agent import BaseAgent

class PlannerAgent(BaseAgent): 
    def __init__(self, llm): 
       super().__init__( 
           llm.with_structured_output( 
               ProjectPlan 
            )
        )


    def run( self, state: ProjectState ) -> ProjectState: 
        prompt = PLANNER_PROMPT.format( requirement=state.requirement ) 
        plan = self.llm.invoke(prompt) 
        state.plan = plan 
        return state