import openai
import json



def generate_quiz_from_summary(summary: str, num_questions: int = 5) -> dict:
    if not summary or len(summary.strip()) < 10:
        print("Summary too short or empty, returning test data")
        return get_test_quiz_data()
        
    prompt = f"""
        You are an expert quiz maker.

        Generate exactly {num_questions} multiple-choice quiz questions based on the following content:

        \"\"\"{summary}\"\"\"

        Each question must include:
        - One clear and concise question.
        - Exactly 3 answer options (labeled A, B, C).
        - One correct answer marked explicitly.

        Return the result as a valid Python dictionary in this format:
        {{
            "questions": [
                {{
                    "question": "Your question here?",
                    "options": ["Option A", "Option B", "Option C"],
                    "answer": "Option A"
                }},
                ...
            ]
        }}

        Do not include any explanations or introductory text—just return the dictionary.
    """

    try: 
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=800,
            temperature=0.7,
        )
        content = response["choices"][0]["message"]["content"].strip()
        print(f"OpenAI response: {content[:100]}...")
        
        # Try to parse the JSON string
        try:
            quiz_data = json.loads(content)
            if "questions" in quiz_data and len(quiz_data["questions"]) > 0:
                return quiz_data
            else:
                print("Invalid quiz data structure, returning test data")
                return get_test_quiz_data()
                
        except json.JSONDecodeError as je:
            print(f"JSON decode error: {je}")
            return get_test_quiz_data()
            
    except Exception as e:
        print(f'Error generating quizzes: {e}')
        return get_test_quiz_data()


def get_test_quiz_data():
    """Return sample quiz data when the API fails"""
    return {
        "questions": [
            {
                "question": "What is the purpose of unit testing?",
                "options": ["To make code look prettier", "To identify bugs early in development", "To slow down the development process"],
                "answer": "To identify bugs early in development"
            },
            {
                "question": "What does PDF stand for?",
                "options": ["Portable Document Format", "Personal Data File", "Program Development Framework"],
                "answer": "Portable Document Format"
            },
            {
                "question": "What is Django?",
                "options": ["A JavaScript library", "A Python web framework", "A database system"],
                "answer": "A Python web framework"
            }
        ]
    }

