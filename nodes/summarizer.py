from langchain_google_genai import ChatGoogleGenerativeAI

from helpers import models
from helpers.template import generate_messages, render_prompt
from schema import ResearchState


async def summarizer(state: ResearchState):
    print("\n[Summarizer] Distilling raw JSON snippets into baselines and gaps...")
    llm_flash = ChatGoogleGenerativeAI(model=models.GEMINI_FLASH_LITE)

    prompt = render_prompt(
        "summarizer.prompt", domain=state["domain"], raw_papers=state["raw_papers"]
    )
    
    messages = generate_messages(prompt)

    summary = await llm_flash.ainvoke(messages)
    return {"gaps_and_baselines": summary.content}
