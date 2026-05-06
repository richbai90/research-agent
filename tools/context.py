import contextvars
from typing import Any, Dict

# ContextVar holds state native to the current async task
_tool_context: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    "tool_context", default={}
)


def get_context() -> Dict[str, Any]:
    """Retrieves the current tool context."""
    return _tool_context.get()


def set_context_var(key: str, value: Any) -> contextvars.Token:
    """Sets a value in the current context."""
    ctx = _tool_context.get().copy()
    ctx[key] = value
    return _tool_context.set(ctx)


def get_context_var(key: str, default: Any = None) -> Any:
    """Retrieves a specific value from the current context."""
    return _tool_context.get().get(key, default)
