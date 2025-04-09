import openai
import time
from openai.error import RateLimitError, APIError, Timeout, ServiceUnavailableError
from issak.utils.summarizers.prompt_loader import get_openai_prompt
def summarize_with_openai(text: str) -> str:
    prompt = get_openai_prompt(text)
    for attempt in range(3):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1500,
            )
            content = response["choices"][0]["message"]["content"]
            return content

        except (RateLimitError, APIError, Timeout, ServiceUnavailableError) as e:
            print(f"OpenAI overload or timeout (attempt {attempt + 1}): {e}")
            time.sleep(3)  

        except Exception as e:
            print(f"Unexpected error: {e}")
            break

        return "⚠️ OpenAI API перегружен. Попробуй чуть позже!"