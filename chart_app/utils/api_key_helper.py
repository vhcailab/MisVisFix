import os

from ..constants.session_key import OPEN_AI_KEY, CLAUDE_KEY, ASST_ID
from ..utils.session_helper import get_session
from .secrets import decrypt_env_var

def get_user_api_keys(request):
    return {
        "openai_key": decrypt_env_var(get_session(request, OPEN_AI_KEY)) if OPEN_AI_KEY in request.session else None,
        "claude_key": decrypt_env_var(get_session(request, CLAUDE_KEY)) if CLAUDE_KEY in request.session else None,
        "asst_id": decrypt_env_var(get_session(request, ASST_ID)) if ASST_ID in request.session else None,
    }

def get_openai_key(request):
    keys = get_user_api_keys(request)
    return keys["openai_key"]

def get_claude_key(request):
    keys = get_user_api_keys(request)
    return keys["claude_key"]

def get_asst_id(request):
    keys = get_user_api_keys(request)
    return keys["asst_id"]