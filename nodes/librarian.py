from langchain_google_genai import ChatGoogleGenerativeAI

from helpers import models
from helpers.template import generate_messages, render_prompt
from schema import ResearchState


async def librarian(state: ResearchState):
    print(f"\n[Optimizer] Refining domain description into a Boolean search query...")
    llm_flash = ChatGoogleGenerativeAI(model=models.GEMINI_FLASH_LITE)

    prompt = render_prompt("librarian.prompt", domain=state["domain"])
    messages = generate_messages(prompt, files=None) # Ensure files is passed if needed

    result = await llm_flash.ainvoke(messages)
    
    raw_content = result.content
    
    if isinstance(raw_content, list):
        # Extract text from parts like [{'type': 'text', 'text': '...'}, ...]
        optimized_query = "".join(
            part["text"] for part in raw_content if isinstance(part, dict) and "text" in part
        )
    else:
        optimized_query = raw_content

    # Clean up formatting
    optimized_query = optimized_query.strip().replace("`", "")

    print(f"[Optimizer] Optimized Query: {optimized_query}")
    return {"optimized_query": optimized_query}
