from langchain_google_genai import ChatGoogleGenerativeAI
from schema import ResearchState
from helpers.template import render_prompt


async def summarizer(state: ResearchState):
    print("\n[Summarizer] Distilling raw JSON snippets into baselines and gaps...")
    llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    prompt = render_prompt(
        "summarizer.prompt", domain=state["domain"], raw_papers=state["raw_papers"]
    )

    summary = await llm_flash.ainvoke(prompt)
    return {"gaps_and_baselines": summary.content}
