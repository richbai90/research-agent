from langchain_google_genai import ChatGoogleGenerativeAI

from helpers.template import generate_messages, render_prompt
from schema import ResearchState


async def orchestrator_node(state: ResearchState):
    llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    cards_str = "\n".join([str(c) for c in state.get("idea_cards", [])])
    time_horizon = state["settings"].get("TIME HORIZON FOR KILLER TEST", "Unknown")

    MAX_ITERATIONS = 4
    current_iteration = state.get("iteration", 1)
    domain = state.get("domain", "Not Provided. Return FAIL")
    gaps_and_baselines = state.get("gaps_and_baselines", "")

    prompt = render_prompt(
        "orchestrator.prompt",
        current_iteration=current_iteration,
        MAX_ITERATIONS=MAX_ITERATIONS,
        cards_str=cards_str,
        time_horizon=time_horizon,
        domain=domain,
        gaps_and_baselines=gaps_and_baselines,
    )

    messages = generate_messages(prompt)

    evaluation = await llm_flash.ainvoke(messages)
    content = evaluation.content

    if "STATUS: FAIL" in content:
        if current_iteration < MAX_ITERATIONS:
            return {"feedback": content, "status": "loop"}
        else:
            if isinstance(content, list):
                content = " ".join(content)
            forced_feedback = (
                content
                + f"\n\n⚠️ **WARNING: Max iterations ({MAX_ITERATIONS}) reached. Outputting best attempt.**"
            )
            return {"feedback": forced_feedback, "status": "final"}

    return {"feedback": content, "status": "final"}
