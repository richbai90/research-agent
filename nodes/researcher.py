from schema import ResearchState
from tools.scite import SciteMCPTool
from tools.context import set_context_var


async def researcher_node(state: ResearchState):
    """Queries Scite via direct JSON-RPC POST using the Boolean query."""

    query = state.get("optimized_query", state["domain"])
    print(f"\n[Scite] Searching literature using: {query}")

    # Injecting the iteration into the global tool context as an example of usage
    set_context_var("current_iteration", state.get("iteration", 0))

    async with SciteMCPTool() as scite_tool:
        raw_results = await scite_tool.execute(query=query)

    return {
        "raw_papers": raw_results,
        "iteration": state.get("iteration", 0) + 1,
    }
