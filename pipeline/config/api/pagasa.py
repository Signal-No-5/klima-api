BASE_URL = "https://www.pagasa.dost.gov.ph"

ACTIVE_WARNING_ENDPOINT = BASE_URL + "/api/ActiveWarning"

ACTIVE_WARNING_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "X-Requested-With": "XMLHttpRequest",
    "Origin": BASE_URL,
    "Referer": BASE_URL,
}
