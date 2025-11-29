import requests

API_URL = "http://127.0.0.1:7860/solve_quiz"


def test_api():
    payload = {
        "email": "test@gmail.com",
        "secret": "TDS2025_Komal_LLM_Quiz!",
        "url": "https://example.com/quiz-1"
    }

    resp = requests.post(API_URL, json=payload)
    print("Status Code:", resp.status_code)
    print("Response:", resp.json())


if __name__ == "__main__":
    test_api()
