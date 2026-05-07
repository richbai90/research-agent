from langchain_google_genai import ChatGoogleGenerativeAI
from helpers import models
from helpers.template import render_prompt
from schema import GenericState, ResearchState
from tools.logger import LoggerTool

history_logger = LoggerTool("DSL_History_Logger", filepath="dsl_history.log")


async def dsl_designer_node(state: GenericState):
    llm = ChatGoogleGenerativeAI(model=models.GEMINI_PRO)
    current_history = history_logger.read_log()
    prompt = render_prompt(
        "dsl_designer.prompt",
        history=current_history,
        task=state.get("domain"),
    )

    response = await llm.ainvoke(prompt)
    output = (
        f"--- [ITERATION {state['iteration']}] ALGEBRAIC CORE ---\n{response.content}"
    )
    await history_logger.execute(output)
    return {"iteration": state["iteration"]}
