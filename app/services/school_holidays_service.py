from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests
from bs4 import BeautifulSoup


PRAEWOOD_TERMDATES_URL = "https://www.praewood.herts.sch.uk/termdatescalendar/term-dates"


class SchoolHolidaysService:
    """Service to fetch and normalize PraeWood School term/holiday dates."""

    def __init__(self, timeout_seconds: int = 10):
        self.timeout_seconds = timeout_seconds

    def _http_get(self, url: str) -> str:
        """HTTP GET with polite headers to avoid basic 403 blocks."""
        headers = {
            # Only a realistic User-Agent is required per target site's behavior
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        }
        resp = requests.get(url, headers=headers, timeout=self.timeout_seconds, allow_redirects=True)
        resp.raise_for_status()
        return resp.text

    def fetch_events_from_website(self) -> List[Dict[str, Any]]:
        """Scrape the official PraeWood Term Dates page for events.

        Robust parsing that handles bold labels, en/em dashes, and varied phrasing.
        Returns a list of events with fields: name, start, end.
        """
        try:
            html = self._http_get(PRAEWOOD_TERMDATES_URL)
            soup = BeautifulSoup(html, "html.parser")
            try:
                print(f"[PraeWood] fetch_events_from_website: html_len={len(html)}")
            except Exception:
                pass

            # Build patterns
            dash = r"[\-\u2013\u2014]"
            weekday_opt = r"(?:Mon(?:day)?|Tue(?:sday)?|Wed(?:nesday)?|Thu(?:rsday)?|Fri(?:day)?|Sat(?:urday)?|Sun(?:day)?)\s+"
            # Allow optional weekday prefixes and optional spaces before ordinal suffixes
            range_pat = re.compile(
                rf"(?:{weekday_opt})?(\d{{1,2}})(?:\s*(?:st|nd|rd|th))?\s+(\w+)\s*{dash}\s+" 
                rf"(?:{weekday_opt})?(\d{{1,2}})(?:\s*(?:st|nd|rd|th))?\s+(\w+)\s+(\d{{4}})",
                re.I,
            )
            range_alt_pat = re.compile(
                rf"(?:{weekday_opt})?(\d{{1,2}})(?:\s*(?:st|nd|rd|th))?\s+(\w+)\s*{dash}\s+" 
                rf"(?:{weekday_opt})?(\d{{1,2}})(?:\s*(?:st|nd|rd|th))?(?:\s+(\w+))?(?:\s+(\d{{4}}))?",
                re.I,
            )
            single_pat = re.compile(
                rf"(?:{weekday_opt})?(\d{{1,2}})(?:\s*(?:st|nd|rd|th))?\s+(\w+)\s+(\d{{4}})",
                re.I,
            )

            def norm_text(t: str) -> str:
                s = (t or "").replace("\u2013", "-").replace("\u2014", "-")
                # collapse excessive whitespace and fix split ordinals like "4 th" -> "4th" for easier matching
                s = re.sub(r"(\d)\s+(st|nd|rd|th)\b", r"\1\2", s, flags=re.I)
                s = re.sub(r"\s+", " ", s)
                return s.strip()

            events: List[Dict[str, Any]] = []

            def parse_date(d: str, mon: str, y: str) -> datetime:
                d = re.sub(r"(st|nd|rd|th)$", "", d, flags=re.IGNORECASE)
                try:
                    return datetime.strptime(f"{d} {mon} {y}", "%d %B %Y")
                except ValueError:
                    # Try abbreviated month
                    return datetime.strptime(f"{d} {mon} {y}", "%d %b %Y")
            # DOM-driven parsing: find label nodes and inspect sibling text for dates
            labels = [
                ("HALF TERM", re.compile(r"^\s*Half\s*Term\s*$", re.I)),
                ("INSET DAY", re.compile(r"^\s*Inset\s*Day\s*$", re.I)),
                ("PUBLIC HOLIDAY", re.compile(r"^\s*Public\s*Holiday\s*$", re.I)),
                ("OCCASIONAL DAY", re.compile(r"^\s*Occasional\s*Day\s*$", re.I)),
            ]

            def try_extract_from_text(lbl: str, text: str) -> bool:
                nonlocal events, matched_count
                s = norm_text(text)
                if not s:
                    return False
                m = range_pat.search(s)
                if m:
                    d1, m1, d2, m2, y = m.groups()
                    start = parse_date(d1, m1, y)
                    end = parse_date(d2, m2, y)
                    events.append({"name": lbl, "start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")})
                    matched_count += 1
                    return True
                m2 = range_alt_pat.search(s)
                if m2:
                    d1, m1, d2, m2_opt, y_opt = m2.groups()
                    y = y_opt or datetime.now().strftime("%Y")
                    end_month = m2_opt or m1
                    start = parse_date(d1, m1, y)
                    end = parse_date(d2, end_month, y)
                    events.append({"name": lbl, "start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")})
                    matched_count += 1
                    return True
                m3 = single_pat.search(s)
                if m3:
                    d, mon, y = m3.groups()
                    dt = parse_date(d, mon, y)
                    events.append({"name": lbl, "start": dt.strftime("%Y-%m-%d"), "end": dt.strftime("%Y-%m-%d")})
                    matched_count += 1
                    return True
                return False

            matched_count = 0
            # Partition by 'Term Dates' headings and parse within each section
            sections = []
            for h2 in soup.find_all('h2'):
                if 'Term Dates' in h2.get_text(' ', strip=True):
                    sections.append(h2)

            def parse_section(start_node):
                # Aggregate text until next h2
                contents: list[str] = []
                node = start_node.next_sibling
                while node is not None and not (getattr(node, 'name', '') == 'h2' and 'Term Dates' in node.get_text(' ', strip=True)):
                    txt = ''
                    if hasattr(node, 'get_text'):
                        txt = node.get_text(' ', strip=True)
                    elif isinstance(node, str):
                        txt = str(node)
                    txt = norm_text(txt)
                    if txt:
                        contents.append(txt)
                    node = node.next_sibling

                # Scan lines: when we see a label line, concatenate following lines until next label/empty and try patterns across the block
                i = 0
                while i < len(contents):
                    line = contents[i]
                    label = None
                    if re.fullmatch(r"(?i)\s*Half\s*Term\s*", line):
                        label = 'HALF TERM'
                    elif re.fullmatch(r"(?i)\s*Inset\s*Day\s*", line):
                        label = 'INSET DAY'
                    elif re.fullmatch(r"(?i)\s*Public\s*Holiday\s*", line):
                        label = 'PUBLIC HOLIDAY'
                    elif re.fullmatch(r"(?i)\s*Occasional\s*Day\s*", line):
                        label = 'OCCASIONAL DAY'

                    if label:
                        block = []
                        j = i + 1
                        while j < len(contents):
                            if re.fullmatch(r"(?i)\s*Half\s*Term\s*|\s*Inset\s*Day\s*|\s*Public\s*Holiday\s*|\s*Occasional\s*Day\s*", contents[j]):
                                break
                            block.append(contents[j])
                            j += 1
                        block_text = ' '.join(block)
                        try:
                            print(f"[PraeWood] label={label} excerpt={block_text[:160]}")
                        except Exception:
                            pass
                        if not try_extract_from_text(label, block_text):
                            # Try line by line as fallback
                            for k in range(i+1, j):
                                if try_extract_from_text(label, contents[k]):
                                    break
                        i = j
                    else:
                        i += 1

            if sections:
                for sec in sections:
                    parse_section(sec)
            else:
                # Fallback: no sections found, parse entire body
                parse_section(soup)

            # Additional robust fallback: full-text line scanning if few/zero matches
            if len(events) == 0:
                try:
                    page_text = soup.get_text("\n", strip=True)
                    page_text = page_text.replace("\u2013", "-").replace("\u2014", "-")
                    lines = [ln for ln in (t.strip() for t in page_text.split("\n")) if ln]
                    print(f"[PraeWood] fallback line-scan lines={len(lines)}")

                    # Expand label detection to inline mentions too
                    label_matchers = [
                        ("HALF TERM", re.compile(r"(^|\b)Half\s*Term(\b|$)", re.I)),
                        ("INSET DAY", re.compile(r"(^|\b)Inset\s*Day(\b|$)", re.I)),
                        ("PUBLIC HOLIDAY", re.compile(r"(^|\b)Public\s*Holiday(\b|$)", re.I)),
                        ("OCCASIONAL DAY", re.compile(r"(^|\b)Occasional\s*Day(\b|$)", re.I)),
                    ]

                    def infer_year(around_idx: int) -> str | None:
                        # Look ±5 lines for a 4-digit year, else current year
                        for delta in range(1, 6):
                            for pos in (around_idx - delta, around_idx + delta):
                                if 0 <= pos < len(lines):
                                    y = re.search(r"\b(20\d{2})\b", lines[pos])
                                    if y:
                                        return y.group(1)
                        return None

                    i = 0
                    while i < len(lines):
                        line = lines[i]
                        matched_label = None
                        for lbl, rx in label_matchers:
                            if rx.search(line):
                                matched_label = lbl
                                break
                        if matched_label is None:
                            i += 1
                            continue

                        # Gather a small window following the label line
                        window = []
                        j = i + 1
                        while j < len(lines) and j < i + 8:  # look ahead up to 7 lines
                            nxt = lines[j]
                            # stop if we hit another known label or a major heading
                            if any(rx.search(nxt) for _, rx in label_matchers) or re.search(r"Term\s*Dates", nxt, re.I):
                                break
                            window.append(nxt)
                            j += 1

                        block_text = " ".join(window)
                        try:
                            print(f"[PraeWood] fallback label={matched_label} excerpt={block_text[:200]}")
                        except Exception:
                            pass

                        # Try patterns on block first
                        if not try_extract_from_text(matched_label, block_text):
                            # Try each line with year inference
                            year_hint = infer_year(i) or datetime.now().strftime("%Y")
                            consumed = False
                            for k, ln in enumerate(window):
                                s = norm_text(ln)
                                m = range_pat.search(s)
                                if m:
                                    d1, m1, d2, m2, y = m.groups()
                                    y_final = y or year_hint
                                    start = parse_date(d1, m1, y_final)
                                    end = parse_date(d2, m2, y_final)
                                    events.append({"name": matched_label, "start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")})
                                    matched_count += 1
                                    consumed = True
                                    break
                                m2 = range_alt_pat.search(s)
                                if m2:
                                    d1, m1, d2, m2_opt, y_opt = m2.groups()
                                    y_final = y_opt or year_hint
                                    end_month = m2_opt or m1
                                    start = parse_date(d1, m1, y_final)
                                    end = parse_date(d2, end_month, y_final)
                                    events.append({"name": matched_label, "start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")})
                                    matched_count += 1
                                    consumed = True
                                    break
                                m3 = single_pat.search(s)
                                if m3:
                                    d, mon, y = m3.groups()
                                    y_final = y or year_hint
                                    dt = parse_date(d, mon, y_final)
                                    events.append({"name": matched_label, "start": dt.strftime("%Y-%m-%d"), "end": dt.strftime("%Y-%m-%d")})
                                    matched_count += 1
                                    consumed = True
                                    break

                            if not consumed:
                                # as very last resort, look for a pattern like "12 Feb - 16 Feb" without year anywhere in window and use hint year
                                m_any = re.search(r"(?:" + weekday_opt + r")?(\d{1,2})(?:\s*(?:st|nd|rd|th))?\s+(\w+)\s*[-]\s*(?:" + weekday_opt + r")?(\d{1,2})(?:\s*(?:st|nd|rd|th))?\s*(\w+)?", block_text, re.I)
                                if m_any:
                                    d1, m1, d2, m2_opt = m_any.groups()
                                    end_month = m2_opt or m1
                                    y_final = year_hint or datetime.now().strftime("%Y")
                                    start = parse_date(d1, m1, y_final)
                                    end = parse_date(d2, end_month, y_final)
                                    events.append({"name": matched_label, "start": start.strftime("%Y-%m-%d"), "end": end.strftime("%Y-%m-%d")})
                                    matched_count += 1

                        i = j
                except Exception as ex:
                    try:
                        print(f"[PraeWood] fallback scan error: {ex}")
                    except Exception:
                        pass

            try:
                print(f"[PraeWood] parsed events: {len(events)}, matched_lines={matched_count}")
            except Exception:
                pass
            return events
        except requests.RequestException as e:
            # Surface as empty; caller can decide caching behavior
            print(f"Error fetching PraeWood term dates: {e}")
            return []

    def extract_holiday_flags(self, start_date: str, end_date: str) -> List[Dict[str, str]]:
        """Normalize scraped events into per-day flags within range.

        Returns list of {date, type, label}.
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            return []

        events = self.fetch_events_from_website()
        flags: List[Dict[str, str]] = []

        for ev in events:
            try:
                ev_start = datetime.strptime(ev["start"], "%Y-%m-%d")
                ev_end = datetime.strptime(ev["end"], "%Y-%m-%d")
            except (KeyError, ValueError):
                continue

            # Clip to requested range
            cur = max(start, ev_start)
            last = min(end, ev_end)
            if cur > last:
                continue

            label = ev.get("name", "SCHOOL HOLIDAY").upper()
            ev_type = "school_holiday"

            while cur <= last:
                flags.append({
                    "date": cur.strftime("%Y-%m-%d"),
                    "type": ev_type,
                    "label": label,
                })
                cur += timedelta(days=1)

        return flags


