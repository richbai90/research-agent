import asyncio
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END

# Import schemas
from schema import ResearchState

# Import nodes
from nodes.librarian import librarian
from nodes.researcher import researcher_node
from nodes.summarizer import summarizer
from nodes.fail_fast_generator import generator_node
from nodes.orchestrator import orchestrator_node
from nodes.hallucination_detector import hallucination_detector

load_dotenv()

# --- GRAPH CONSTRUCTION ---

builder = StateGraph(ResearchState)
builder.add_node("optimize_query", librarian)
builder.add_node("research", researcher_node)
builder.add_node("summarize", summarizer)
builder.add_node("generate", generator_node)
builder.add_node("orchestrate", orchestrator_node)
builder.add_node("hallucination_detector", hallucination_detector)

builder.add_edge(START, "optimize_query")
builder.add_edge("optimize_query", "research")
builder.add_edge("research", "summarize")
builder.add_edge("summarize", "generate")
builder.add_edge("generate", "orchestrate")

builder.add_conditional_edges(
    "orchestrate", lambda state: state["status"], {"loop": "generate", "final": END}
)

builder.add_conditional_edges(
    "hallucination_detector",
    lambda state: state["status"],
    {"loop": "generate", "final": END},
)

graph = builder.compile()

# Note: You can remove the main() boilerplate here if you are solely executing via Streamlit.


async def main():
    initial_state = {
        "domain": "Neuromorphic sensor data processing",
        "settings": {
            "TARGET OUTPUT COUNT": 3,
            "TIME HORIZON FOR KILLER TEST": "1 week",
            "RESOURCE BOUNDARY": "No cluster access, single GPU only",
        },
        "iteration": 0,
        "status": "continue",
    }

    print("Starting Research Agent...")
    async for chunk in graph.astream(initial_state):
        for node, values in chunk.items():
            print(f"--- Completed Node: {node} ---")
            if node == "orchestrate":
                print(f"Decision: {values.get('status')}")
                if values.get("status") == "final":
                    print("\nFinal output reached.")


if __name__ == "__main__":
    asyncio.run(main())
