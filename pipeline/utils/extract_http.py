import time

from requests import request
from requests.exceptions import JSONDecodeError, RequestException


def extract_http(
    method: str,
    source: str,
    headers: dict = None,
    retry: int = 3,
    delay: int = 5,
    timeout: int = 10,
    **kwargs,
):
    """
    Fetches and validates an API response with retries,
    ensuring JSON validity and graceful error handling.

    Args:
        method (str): HTTP method ("GET", "POST", etc.).
        source (str): API endpoint.
        headers (dict): Optional HTTP headers.
        retries (int): Number of retry attempts.
        delay (int): Delay (seconds) between retries.
        timeout (int): Request timeout (seconds).

    Returns:
        dict/list: Parsed JSON data.

    Raises:
        Exception: Descriptive error message if request fails.
    """

    for attempt in range(1, retry + 1):
        try:
            print(f"🔄 Fetching from {source} (attempt {attempt})...")
            response = request(
                method, source, headers=headers, timeout=timeout, **kwargs
            )

            # Check HTTP status
            if response.status_code != 200:
                raise Exception(f"{source} returned HTTP {response.status_code}")

            # Validate JSON
            try:
                data = response.json()
            except JSONDecodeError:
                snippet = response.text[:200].replace("\n", " ")
                if snippet:
                    snippet = f"non-JSON response. Preview: {snippet}"
                else:
                    snippet = "empty data."
                raise Exception(
                    f"Response status: {response.status_code}\n"
                    f"{source} returned {snippet}\n"
                )

            print(f"✅ Successfully fetched from {source}.\n")
            return data

        except RequestException as e:
            print(f"⚠️ Network error from {source}: {e}")
        except Exception as e:
            print(f"⚠️ {e}")

        # Only sleep if not the last attempt
        if attempt < retry:
            print(f"⏳ Retrying in {delay} seconds...")
            time.sleep(delay)

    raise Exception(f"❌ Failed to fetch from {source} after {retry} attempts.")
