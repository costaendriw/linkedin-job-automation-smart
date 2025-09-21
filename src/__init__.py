__version__ = "2.0.0"
__author__ = "LinkedIn Automation Team"
__description__ = "Sistema inteligente de automação para vagas do LinkedIn"

# Importações principais para facilitar o uso
from .automation_fixed import LinkedInAutomation
from .gui import LinkedInGUI
from .utils import (
    random_delay,
    async_random_delay,
    safe_click,
    safe_fill,
    validate_email,
    clean_text,
    format_job_count
)

__all__ = [
    'LinkedInAutomation',
    'LinkedInGUI',
    'random_delay',
    'async_random_delay',
    'safe_click',
    'safe_fill',
    'validate_email',
    'clean_text',
    'format_job_count'
]