import openai


def generate_stream_response(prompt: str):
    try:
        response_iter = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in response_iter:
            if "content" in chunk["choices"][0]["delta"]:
                text_piece = chunk["choices"][0]["delta"]["content"]
                yield f"data: {text_piece}\n\n"
    except Exception as e:

        yield f"data: [Error: {str(e)}]\n\n"