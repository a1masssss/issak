import openai


def generate_flashcards_from_summary(summary: str) -> list:
    try:
        prompt = f"""
        You are tasked with creating exactly 10 educational flashcards from the following text:
        {summary}
        Format:
        Q: Question 1
        A: Answer 1
        Q: Question 2
        A: Answer 2
        ...
        Q: Question 10
        A: Answer 10

        Generate only 10 flashcards with no additional text or explanations.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            max_tokens=1200,
        )

        flashcards_raw = response["choices"][0]["message"]["content"]
        flashcards = []
        lines = flashcards_raw.split("\n")
        lines = [line.strip() for line in lines if line.strip()]

        for i in range(0, len(lines) - 1, 2):
            if lines[i].startswith("Q:") and lines[i + 1].startswith("A:"):
                question = lines[i].replace("Q:", "").strip()
                answer = lines[i + 1].replace("A:", "").strip()
                if question and answer:
                    flashcards.append({"question": question, "answer": answer})

        return flashcards

    except Exception as e:
        print(f"Error generating flashcards: {e}")
        return []








