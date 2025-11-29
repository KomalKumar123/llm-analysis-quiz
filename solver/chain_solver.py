import time
from solver.single_solver import solve_single_quiz


def solve_quiz_chain(start_url: str, email: str, secret: str, max_time: int = 150) -> dict:
    """
    Solves chained quizzes within time limit.
    """
    start = time.time()
    current_url = start_url
    last_result = None

    while current_url and time.time() - start < max_time:
        result = solve_single_quiz(current_url, email, secret)
        last_result = result

        if result.get("correct") is True:
            current_url = result.get("url")  # next quiz if available
        elif result.get("correct") is False:
            next_url = result.get("url")
            if next_url:
                current_url = next_url
            else:
                break
        else:
            break

    return last_result or {"error": "No result"}
