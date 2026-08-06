from langgraph.graph import ( StateGraph, START, END )
from state import ProjectState 
from agents.planner import PlannerAgent
from agents.architect import ArchitectAgent
from agents.coder import CoderAgent
from agents.tester import TesterAgent
from nodes.writer import writer_node
from nodes.queue import initialize_queue
from nodes.router import has_pending_files
from nodes.runner import runner_node
from agents.fixer import FixAgent
from nodes.router import fix_router
from agents.reviewer import ReviewerAgent
from llm import llm

planner = PlannerAgent(llm)
architect = ArchitectAgent(llm)
coder = CoderAgent()
tester = TesterAgent(llm)
fixer = FixAgent(llm)
reviewer = ReviewerAgent(llm)
builder = StateGraph(ProjectState)


builder.add_node( "planner", planner.run )
builder.add_node( "architect", architect.run )
builder.add_node( "coder", coder.run)
builder.add_node( "queue", initialize_queue )
builder.add_node( "writer", writer_node )
builder.add_node( "runner", runner_node )
builder.add_node( "tester",tester.run)
builder.add_node( "fixer", fixer.run )
builder.add_node(
    "reviewer",
    reviewer.run
)

builder.add_edge( START, "planner" )
builder.add_edge( "planner", "architect" )
builder.add_edge( "architect", "queue" )
builder.add_edge( "queue", "coder" )
builder.add_edge( "coder", "writer" )
builder.add_conditional_edges(
    "writer",
    has_pending_files,
    {
        "queue": "queue",
        "end": "runner"
    }
)

builder.add_edge(
    "runner",
    "tester"
)

builder.add_edge(
    "fixer",
    "writer"
)

builder.add_edge(
    "writer",
    "runner"
)

builder.add_edge(
    "runner",
    "tester"
)

builder.add_conditional_edges(
    "tester",
    fix_router,
    {
        "completed": END,
        "fixer": "fixer",
        "failed": END
    }
)

graph = builder.compile()