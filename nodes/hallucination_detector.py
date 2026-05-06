from langchain_anthropic import ChatAnthropic
from schema import ResearchState
from helpers.template import render_prompt


async def hallucination_detector(state: ResearchState):
    """Final pipeline check to ensure Claude doesn't catch Gemini hallucinating literature."""
    print("\n[Reviewer] Claude is verifying cards against ground-truth literature...")

    llm_claude = ChatAnthropic(model="claude-3-5-sonnet-latest")

    cards_str = "\n".join([str(c) for c in state.get("idea_cards", [])])
    current_iteration = state.get("iteration", 0)

    MAX_PIPELINE_ITERATIONS = 5

    prompt = render_prompt(
        "hallucination-detector.prompt",
        domain=state["domain"],
        gaps_and_baselines=state.get("gaps_and_baselines", "NO LITERATURE PROVIDED"),
        cards_str=cards_str,
    )

    evaluation = await llm_claude.ainvoke(prompt)
    content = evaluation.content

    # The prompt guarantees one of these strings will be printed at the top
    if "STATUS: HALLUCINATION" in content:
        if current_iteration < MAX_PIPELINE_ITERATIONS:
            print(f"[Reviewer] Hallucination caught! Forcing correction loop.")
            new_feedback = (
                f"🚨 CRITICAL HALLUCINATION DETECTED BY CLAUDE REVIEWER:\n{content}"
            )
            return {"feedback": new_feedback, "status": "loop"}
        else:
            print(
                f"[Reviewer] Max iterations reached. Appending hallucination warning to final output."
            )
            forced_feedback = (
                state.get("feedback", "")
                + f"\n\n⚠️ **HALLUCINATION WARNING:**\n{content}"
            )
            return {"feedback": forced_feedback, "status": "final"}

    print("[Reviewer] Cards are clean and grounded.")
    success_feedback = (
        state.get("feedback", "") + "\n\n✅ **Hallucination Check:** Passed."
    )
    return {"feedback": success_feedback, "status": "final"}
