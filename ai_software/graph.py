from langgraph.graph import ( StateGraph, START, END )
from state import ProjectState 
from nodes.writer import writer_node
from nodes.queue import initialize_queue
from nodes.router import has_pending_files
from nodes.runner import runner_node
from nodes.router import fix_router

from services.container import ServiceContainer

container = ServiceContainer()
builder = StateGraph(ProjectState)


builder.add_node( "planner", container.planner.run )
builder.add_node( "architect", container.architect.run )
builder.add_node( "coder", container.coder.run)
builder.add_node( "queue", initialize_queue )
builder.add_node( "writer", writer_node )
builder.add_node( "runner", runner_node )
builder.add_node( "tester",container.tester.run)
builder.add_node( "fixer", container.fixer.run )
builder.add_node(
    "reviewer",
    container.reviewer.run
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
        "queue": "coder",
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

builder.add_conditional_edges(
    "tester",
    fix_router,
    {
        "completed": "reviewer",
        "fixer": "fixer",
        "failed": END
    }
)

builder.add_edge( "reviewer", END )

graph = builder.compile()