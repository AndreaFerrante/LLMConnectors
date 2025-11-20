import sys
import logging
from typing import Optional

def setup_logging(verbose: bool = False, log_file: Optional[str] = None):

    """
    Configure logging based on verbosity level.
    """

    level    = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
