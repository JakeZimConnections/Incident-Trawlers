# Sets up terminal logging for the "trawlers" logger, so log() and trace summaries show up next to uvicorn's output.
import logging

from app.core.config import settings


def setup_logging() -> None:
    """Print the "trawlers" logger to the terminal as `HH:MM:SS LEVEL message`."""
    logger = logging.getLogger("trawlers")
    if logger.handlers:  # already set up (e.g. uvicorn --reload re-imports)
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(handler)
    logger.setLevel(settings.log_level.upper())
    logger.propagate = False  # don't print twice via the root logger
