from langchain_google_genai import ChatGoogleGenerativeAI
from schema import ResearchState
from helpers.template import render_prompt


async def orchestrator_node(state: ResearchState):
    llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    cards_str = "\n".join([str(c) for c in state.get("idea_cards", [])])
    time_horizon = state["settings"].get("TIME HORIZON FOR KILLER TEST", "Unknown")

    MAX_ITERATIONS = 4
    current_iteration = state.get("iteration", 1)

    prompt = render_prompt(
        "orchestrator.prompt",
        current_iteration=current_iteration,
        max_iterations=MAX_ITERATIONS,
        cards_str=cards_str,
        time_horizon=time_horizon,
    )

    evaluation = await llm_flash.ainvoke(prompt)
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
