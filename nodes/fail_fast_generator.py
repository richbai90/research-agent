import asyncio

from google import genai
from google.genai.client import Client
from google.genai.types import FileState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from streamlit.runtime.uploaded_file_manager import UploadedFile

from helpers import models
from helpers.template import generate_messages, render_prompt
from schema import GenerationOutput, ResearchState


async def upload_file(file: UploadedFile, client: Client):
    uploaded_file = client.files.upload(file=file, config={'mime_type': file.type or 'application/pdf'}) 
    while uploaded_file.state == FileState.PROCESSING:
       await asyncio.sleep(0.1)

    if uploaded_file.name:
         return client.files.get(name=uploaded_file.name)
    return None

async def generator_node(state: ResearchState):
    current_iteration = state.get("iteration", 0) + 1

    client = genai.Client()
    files = [asyncio.create_task(upload_file(file, client)) for file in state['context_files']]
    files = [ f for f in await asyncio.gather(*files) if f is not None]
    llm_pro = ChatGoogleGenerativeAI(model=models.GEMINI_PRO)
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

    messages = generate_messages(prompt, files)


    result = await structured_llm.ainvoke(messages)

    return {
        "idea_cards": [card.model_dump() for card in result.idea_cards],
        "iteration": current_iteration,
    }
