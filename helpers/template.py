import os
from jinja2 import Environment, FileSystemLoader

# Resolve the absolute path to the 'prompts' directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS_DIR = os.path.join(BASE_DIR, "prompts")

# Initialize the Jinja environment
env = Environment(
    loader=FileSystemLoader(PROMPTS_DIR), trim_blocks=True, lstrip_blocks=True
)


def render_prompt(template_name: str, **kwargs) -> str:
    """Loads a .prompt file and renders it with the provided keyword arguments."""
    template = env.get_template(template_name)
    return template.render(**kwargs)
