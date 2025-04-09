import openai


def generate_title_from_text(text:str) -> str:
    prompt = f"""
    Generate a concise, capitalized title (3-5 words) for the following text:
    "{text}"

    Output ONLY the title (3-5 words), with no extra commentary, explanation, or formatting.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=15,
            temperature=0.3,
        )
        return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"Error generating title: {e}")
        return "Untitled"