from langchain_google_genai import ChatGoogleGenerativeAI
from schema import ResearchState
from helpers.template import render_prompt


async def librarian(state: ResearchState):
    print(f"\n[Optimizer] Refining domain description into a Boolean search query...")
    llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    prompt = render_prompt("librarian.prompt", domain=state["domain"])

    result = await llm_flash.ainvoke(prompt)
    optimized_query = result.content.strip().replace("`", "")

    print(f"[Optimizer] Optimized Query: {optimized_query}")
    return {"optimized_query": optimized_query}
