import shutil
import logging
from typing import Optional
from config.settings import DEPENDENCIES

def check_dependency(command: str, name: str, install_instructions: str) -> Optional[str]:
    """Checks if a dependency is installed or not.

    Args:
        command (str): command used to check for the dependency
        name (str): the package name of the dependency
        install_instructions (str): the instruction used to install the package

    Returns:
        Optional[str]: Error message if dependency is missing, None otherwise
    """
    if not shutil.which(command):
        error_msg = f"{name} is required but not installed!\n\nInstall it using:\n{install_instructions}"
        logging.error(error_msg)
        return error_msg
    return None

def check_all_dependencies() -> bool:
    """Checks if all dependencies exist or not.

    Returns:
        bool: returns false if there are dependencies missing, or return true
    """
    missing = [check_dependency(cmd, name, inst) for cmd, name, inst in DEPENDENCIES]
    missing = [msg for msg in missing if msg]
    return not missing 