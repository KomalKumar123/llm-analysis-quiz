import requests

def submit_answer(submit_url: str, payload: dict) -> dict:
    """
    Sends the final answer to the quiz submit endpoint.
    """
    response = requests.post(submit_url, json=payload, timeout=30)
    response.raise_for_status()

    try:
        return response.json()
    except Exception:
        return {"raw_response": response.text}
