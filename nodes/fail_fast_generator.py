from langchain_google_genai import ChatGoogleGenerativeAI
from schema import ResearchState, GenerationOutput
from helpers.template import render_prompt


async def generator_node(state: ResearchState):
    current_iteration = state.get("iteration", 0) + 1

    llm_pro = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
    structured_llm = llm_pro.with_structured_output(GenerationOutput)

    settings_str = "\n".join([f"- {k}: {v}" for k, v in state["settings"].items()])
    time_horizon = state["settings"].get("TIME HORIZON FOR KILLER TEST", "Unknown")
    target_output_count = state["settings"].get("TARGET OUTPUT COUNT", 3)

    prompt = render_prompt(
        "fail-fast.prompt",
        domain=state["domain"],
        settings_str=settings_str,
        time_horizon=time_horizon,
        gaps_and_baselines=state.get("gaps_and_baselines", ""),
        feedback=state.get("feedback", "None"),
        target_output_count=target_output_count,
    )

    result = await structured_llm.ainvoke(prompt)

    return {
        "idea_cards": [card.model_dump() for card in result.idea_cards],
        "iteration": current_iteration,
    }
