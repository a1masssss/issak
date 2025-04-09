from pathlib import Path
from django.conf import settings

def get_openai_prompt(text: str) -> str:
    prompt_path = Path(settings.BASE_DIR) / "issak" / "utils" / "summarizers" / "prompts" / "openai_prompt.txt"
    template = prompt_path.read_text(encoding="utf-8")
    return template.format(text=text)
