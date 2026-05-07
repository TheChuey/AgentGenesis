# backend/prompts.py
from pathlib import Path
import re

PROMPT_FILE = Path(__file__).parent.parent / "resources" / "system_prompts.md"
CORE_KNOWLEDGE_FILE = Path(__file__).parent / "instructions" / "core_knowledge.md"

def get_core_knowledge() -> str:
    """Reads core knowledge about the user from the instructions folder."""
    if CORE_KNOWLEDGE_FILE.exists():
        return CORE_KNOWLEDGE_FILE.read_text(encoding="utf-8").strip()
    return ""

from moduels.tools.time_tool import get_current_datetime

def get_system_prompt(section_name: str = "CODING_ASSISTANT") -> str:
    base_prompt = "You are a helpful AI assistant."
    
    if PROMPT_FILE.exists():
        content = PROMPT_FILE.read_text(encoding="utf-8")
        # Find the text between # SECTION_NAME and the next # or end of file
        pattern = rf"# {section_name}\s*(.*?)(?=\n#|$)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            base_prompt = match.group(1).strip()
            
    # Inject Core Knowledge automatically
    knowledge = get_core_knowledge()
    if knowledge:
        base_prompt += f"\n\n[SYSTEM CORE KNOWLEDGE]\n{knowledge}"
        
    # Inject Current Time
    current_time = get_current_datetime()
    base_prompt += f"\n\n[CURRENT SYSTEM TIME]\nThe current local date and time is: {current_time}"
        
    return base_prompt