from llm import llm 
from agents.planner import PlannerAgent 
from agents.architect import ArchitectAgent 
from agents.coder import CoderAgent 
from agents.tester import TesterAgent 
from agents.fixer import FixAgent 
from agents.reviewer import ReviewerAgent 

class ServiceContainer: 
    def __init__(self): 
        self.llm = llm 
        self.planner = PlannerAgent( self.llm ) 

        self.architect = ArchitectAgent( self.llm ) 
        self.coder = CoderAgent( self.llm ) 
        self.tester = TesterAgent( self.llm ) 
        self.fixer = FixAgent( self.llm ) 
        self.reviewer = ReviewerAgent( self.llm )