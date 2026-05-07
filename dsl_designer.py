import os
import asyncio
from langgraph.graph import StateGraph, START, END
from schema import GenericState
from nodes.math_specialist import math_specialist_node
from nodes.physics_expert import physics_expert_node
from nodes.dsl_specialist import dsl_designer_node
from tools.logger import LoggerTool
from dotenv import load_dotenv

load_dotenv()

history_logger = LoggerTool("DSL_History_Logger", filepath="dsl_history.log")


def evaluate_feedback(state: GenericState):
    current_log = history_logger.read_log()

    if "[DECISION: SATISFIED]" in current_log:
        return END
    if state["iteration"] > 5:
        print("\n⚠️ Max iterations reached. Forcing exit.")
        return END

    return "Agent_1_Algebraic_Core"


def build_cli_graph():
    builder = StateGraph(GenericState)
    builder.add_node("Agent_1_Algebraic_Core", math_specialist_node)
    builder.add_node("Agent_2_Syntax_Architect", dsl_designer_node)
    builder.add_node("Agent_3_Physics_Theorist", physics_expert_node)

    builder.add_edge(START, "Agent_1_Algebraic_Core")
    builder.add_edge("Agent_1_Algebraic_Core", "Agent_2_Syntax_Architect")
    builder.add_edge("Agent_2_Syntax_Architect", "Agent_3_Physics_Theorist")
    builder.add_conditional_edges("Agent_3_Physics_Theorist", evaluate_feedback)

    return builder.compile()


async def main():
    task_description = """Define the specification for a "Physics-First" DSL built on symbolic linear algebra.
    Constraints: No inheritance; use composition and interfaces. No imperative keywords (for, while, if/else). The final output should be a draft EBNF grammar and a code example of a 4f imaging system."""

    print("🚀 Initiating Multi-Agent DSL Design Loop...\n")

    # Safely clear the log at the start of orchestration, outside of the tool logic
    if os.path.exists(history_logger.filepath):
        os.remove(history_logger.filepath)

    graph = build_cli_graph()
    initial_state: GenericState = {
        "domain": task_description,
        "iteration": 1,
        "feedback": "",
        "settings": {},
        "status": "continue",
    }

    async for chunk in graph.astream(initial_state):
        for node_name in chunk.keys():
            print(f"✅ COMPLETED: {node_name}")

    print(
        f"\nProcess finished. Full design specification written to {history_logger.filepath}"
    )


if __name__ == "__main__":
    asyncio.run(main())
