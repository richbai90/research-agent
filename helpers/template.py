import os

from google.genai.types import File
from jinja2 import Environment, FileSystemLoader
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import MessageLike
from pydantic import BaseModel

# Resolve the absolute path to the 'prompts' directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

# Initialize the Jinja environment
env = Environment(
    loader=FileSystemLoader(PROMPTS_DIR), trim_blocks=True, lstrip_blocks=True
)


class Prompt(BaseModel):
    system: str
    user: str

def render_prompt(template_name: str, **kwargs) -> Prompt:
    """Loads a .prompt file and renders it with the provided keyword arguments."""
    template = env.get_template(template_name)
    content = template.render(**kwargs)
    
    # Use a split limit of 1 to ensure everything after the first === 
    # is captured in the user prompt, even if the domain contains ===
    prompts = content.split("===", 1)
    
    if len(prompts) == 2:
        system_part = prompts[0].strip()
        # Clean up any leftover separator chars and whitespace from the second part
        user_part = prompts[1].lstrip('=').strip()
        return Prompt(system=system_part, user=user_part)
    
    return Prompt(system="", user=content.strip())

def generate_messages(prompt: Prompt, files: list[File] | None = None) -> LanguageModelInput: 
    if not files:
        files = []
    messages  = []
    if prompt.system != "":
        messages.append(SystemMessage(prompt.system))


    content = [{"type": "text", "text": prompt.user}]
    # 2. Add the media blocks for each uploaded file
    for file in files:
        content.append({
            "type": "media",
            "file_uri": file.uri or "",
            "mime_type": file.mime_type or "",
        })

    messages.append(HumanMessage(content))

    return messages
