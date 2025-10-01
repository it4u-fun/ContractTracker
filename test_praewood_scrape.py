import re
import sys

import requests

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Please install beautifulsoup4: pip install beautifulsoup4")
    raise


URL = "https://www.praewood.herts.sch.uk/termdatescalendar/term-dates"


def fetch_html() -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    }
    resp = requests.get(URL, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.text


def normalize_lines(html: str):
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text("\n", strip=True)
    # normalize dashes
    text = text.replace("\u2013", "-").replace("\u2014", "-")
    lines = [ln.strip() for ln in text.split("\n") if ln and ln.strip()]
    return lines


def test_regex(lines):
    weekday_opt = r"(?:Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)\s+"
    half_term_regex = re.compile(
        rf"Half\s*Term\s+(?:{weekday_opt})?(\d{{1,2}})(?:st|nd|rd|th)?\s+(\w+)\s*[\-]\s+(?:{weekday_opt})?(\d{{1,2}})(?:st|nd|rd|th)?\s+(\w+)\s+(\d{{4}})",
        flags=re.IGNORECASE,
    )
    half_term_alt = re.compile(
        rf"Half\s*Term\s+(?:{weekday_opt})?(\d{{1,2}})(?:st|nd|rd|th)?\s+(\w+)\s*[\-]\s+(?:{weekday_opt})?(\d{{1,2}})(?:st|nd|rd|th)?\s*(\w+)?\s*(\d{{4}})?",
        flags=re.IGNORECASE,
    )
    single_day_regex = re.compile(
        r"\b(Inset Day|Public Holiday|Occasional Day)\b.*?(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)\s+(\d{4})",
        flags=re.IGNORECASE,
    )

    matched = []
    for ln in lines:
        if half_term_regex.search(ln) or half_term_alt.search(ln) or single_day_regex.search(ln):
            matched.append(ln)

    print(f"lines={len(lines)}, matched_lines={len(matched)}")
    for ln in matched[:20]:
        print("MATCH:", ln)


if __name__ == "__main__":
    html = fetch_html()
    print(f"html_len={len(html)}")
    lines = normalize_lines(html)
    print(f"lines_norm={len(lines)}")
    # sample lines containing keywords
    sample = [ln for ln in lines if any(k in ln for k in ["Half", "Inset", "Public Holiday", "Occasional"])]
    print("sample count:", len(sample))
    for ln in sample[:20]:
        print("SAMPLE:", ln)
    print("---- regex test ----")
    test_regex(lines)


