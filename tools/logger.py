import logging
import os
from tools.base import BaseTool


class LoggerTool(BaseTool):
    name = "Logger"
    description = "A Logger for writing outputs to disk and reading history"

    def __init__(self, name: str, filepath: str = "dsl_history.log") -> None:
        super().__init__()
        self.name = name
        self.filepath = filepath
        self.logger = logging.getLogger(self.name)

        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            # Strictly use 'a' (append) to prevent accidental truncations
            fh = logging.FileHandler(self.filepath, mode="a")
            formatter = logging.Formatter("%(message)s\n")
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)

    async def execute(
        self, message: str = "", level: int = logging.INFO, **kwargs
    ) -> None:
        match level:
            case logging.DEBUG:
                self.logger.debug(message)
            case logging.INFO:
                self.logger.info(message)
            case logging.WARN:
                self.logger.warning(message)
            case logging.ERROR:
                self.logger.error(message)

    def read_log(self) -> str:
        """Reads the current state of the log file to pass to the prompt."""
        if not os.path.exists(self.filepath):
            return "(No history yet. This is the first pass.)"
        with open(self.filepath, "r") as f:
            content = f.read().strip()
            return content if content else "(No history yet. This is the first pass.)"
