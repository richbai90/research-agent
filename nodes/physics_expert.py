from langchain_google_genai import ChatGoogleGenerativeAI
from helpers import models
from helpers.template import render_prompt  # Utilizing existing helper
from schema import GenericState
from tools.logger import LoggerTool

history_logger = LoggerTool("DSL_History_Logger", filepath="dsl_history.log")


async def physics_expert_node(state: GenericState):
    llm = ChatGoogleGenerativeAI(model=models.GEMINI_PRO, temperature=0.1)
    current_history = history_logger.read_log()
    prompt = render_prompt(
        "physics-expert.prompt", task=state["domain"], history=current_history
    )
    response = await llm.ainvoke(prompt)

    output = (
        f"--- [ITERATION {state['iteration']}] PHYSICS THEORIST ---\n{response.content}"
    )
    await history_logger.execute(output)
    return {"iteration": state["iteration"] + 1}
