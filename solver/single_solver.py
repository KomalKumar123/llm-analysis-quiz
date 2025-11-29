import re
import base64
from typing import Tuple, Optional
from urllib.parse import urljoin

from tools.browser_utils import load_quiz_page
from tools.downloader import download_file
from tools.data_ops import compute_from_csv, compute_from_pdf
from tools.submitter import submit_answer


def _decode_atob_blocks(html: str) -> str:
    """
    Find any atob(`...`) or atob("...") in the HTML, base64-decode them
    and concatenate for further parsing.
    """
    decoded_parts = []

    # Backtick-delimited base64
    for m in re.finditer(r"atob\(\s*`([^`]+)`\s*\)", html):
        try:
            decoded = base64.b64decode(m.group(1)).decode("utf-8", errors="ignore")
            decoded_parts.append(decoded)
        except Exception:
            pass

    # Quote-delimited base64 (single or double)
    for m in re.finditer(r"atob\(\s*['\"]([^'\"]+)['\"]\s*\)", html):
        try:
            decoded = base64.b64decode(m.group(1)).decode("utf-8", errors="ignore")
            decoded_parts.append(decoded)
        except Exception:
            pass

    return "\n".join(decoded_parts)


def _find_submit_and_file(html: str, text: str, decoded: str, quiz_url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Try to find submit URL and file URL from:
      - raw HTML
      - rendered text
      - any atob(...) decoded content.
    Returns (submit_url, file_url_or_None).
    """
    search_space = html + "\n" + decoded + "\n" + text

    # 1) Try full absolute submit URL first
    submit_match = re.search(
        r"(https?://[^\s\"'<>]*submit[^\s\"'<>]*)",
        search_space,
        re.IGNORECASE,
    )
    submit_url = submit_match.group(1) if submit_match else None

    # 2) If not found, handle relative like "/submit"
    if not submit_url:
        rel_match = re.search(r"\b/submit\b", search_space)
        if rel_match:
            submit_url = urljoin(quiz_url, "/submit")

    # File URL: support csv, pdf, json, txt, xlsx
    file_match = re.search(
        r"(https?://[^\s\"'<>]+\.(csv|pdf|json|txt|xlsx))",
        search_space,
        re.IGNORECASE,
    )
    file_url = file_match.group(1) if file_match else None

    return submit_url, file_url


def _compute_answer_from_file(file_url: str) -> float:
    """
    Download the file and compute a reasonable default answer.
    For now:
    - CSV  -> sum of 'value' column
    - PDF  -> sum of the first numeric column on first page
    - JSON/TXT/XLSX -> currently not implemented; returns 0
    """
    file_bytes = download_file(file_url)

    if file_url.lower().endswith(".csv"):
        # Sum of 'value' column by default
        return compute_from_csv(file_bytes, operation="sum", column="value")

    if file_url.lower().endswith(".pdf"):
        # Sum of first column on first page
        return compute_from_pdf(file_bytes, page_no=0, column_index=0)

    # For now: JSON/TXT/XLSX not implemented -> return 0 as a fallback
    return 0.0


def solve_single_quiz(quiz_url: str, email: str, secret: str) -> dict:
    """
    Solves one quiz URL and submits the answer.

    Strategy:
    1. Load page (JS rendered) with Playwright.
    2. Extract submit URL and file URL from HTML, text, and any atob(...) decoded content.
    3. If a file URL is found, compute answer from the file.
    4. If not, send a fallback answer ("hello" or 0).
    5. Submit answer and return the submitter's response.
    """
    page_data = load_quiz_page(quiz_url)
    html = page_data["html"]
    text = page_data["text"]

    # Decode any base64-encoded atob(...) content (for real quiz pages)
    decoded = _decode_atob_blocks(html)

    # Find submit and file URLs
    submit_url, file_url = _find_submit_and_file(html, text, decoded, quiz_url)

    if not submit_url:
        # No submit URL: we cannot proceed properly
        return {"error": "Submit URL not found on quiz page", "quiz_url": quiz_url}

    # Decide answer
    if file_url:
        try:
            answer = _compute_answer_from_file(file_url)
        except Exception:
            # If computation fails, still send a best-effort fallback
            answer = 0.0
    else:
        # No downloadable file found: demo page says "anything you want"
        # To be safe, we send a simple string.
        answer = "hello"

    # Build submission payload
    payload = {
        "email": email,
        "secret": secret,
        "url": quiz_url,
        "answer": answer,
    }

    # Submit to the quiz's submit endpoint
    submit_result = submit_answer(submit_url, payload)

    # Wrap and return
    return {
        "quiz_url": quiz_url,
        "submit_url": submit_url,
        "file_url": file_url,
        "answer_sent": answer,
        **submit_result
    }
