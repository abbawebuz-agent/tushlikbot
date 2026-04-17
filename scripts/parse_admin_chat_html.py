import argparse
import html
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


PROMPT_USER_ID = "Xodim user_id sini jo'nating"
PROMPT_FULL_NAME = "Xodim to'liq ismini kiriting"


_FROM_RE = re.compile(r'<div class="from_name">\s*(.*?)\s*</div>', re.S)
_TEXT_RE = re.compile(r'<div class="text">\s*(.*?)\s*</div>', re.S)
_DATE_TITLE_RE = re.compile(r'<div class="pull_right date details" title="([^"]+)"', re.S)
_TAG_RE = re.compile(r"<[^>]+>")


def _clean_html_text(raw: str) -> str:
    if raw is None:
        return ""
    # Telegram export uses <br/> for newlines and sometimes wraps commands in <a>.
    raw = raw.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    raw = _TAG_RE.sub("", raw)
    return html.unescape(raw).strip()


@dataclass(frozen=True)
class ChatMessage:
    from_name: str
    text: str
    date_title: Optional[str]

    @property
    def parsed_dt(self) -> Optional[str]:
        """
        Keep original title when possible; also provide ISO8601-like string if parsing succeeds.
        Example title: "28.10.2023 20:51:02 UTC+05:00"
        """
        if not self.date_title:
            return None
        m = re.match(r"(\d{2})\.(\d{2})\.(\d{4}) (\d{2}):(\d{2}):(\d{2}) UTC([+-]\d{2}):(\d{2})", self.date_title)
        if not m:
            return self.date_title
        dd, mm, yyyy, hh, mi, ss, tzh, tzm = m.groups()
        # Keep offset, but normalize to "+HH:MM" format.
        return f"{yyyy}-{mm}-{dd}T{hh}:{mi}:{ss}{tzh}:{tzm}"


def iter_default_message_blocks(html_text: str) -> Iterable[str]:
    """
    Split Telegram HTML export into chunks for each "message default clearfix".
    This is robust enough for Telegram's consistent export format.
    """
    marker = '<div class="message default clearfix"'
    starts = [m.start() for m in re.finditer(re.escape(marker), html_text)]
    if not starts:
        return
    starts.append(len(html_text))
    for i in range(len(starts) - 1):
        yield html_text[starts[i] : starts[i + 1]]


def parse_messages_from_html_file(path: Path) -> List[ChatMessage]:
    text = path.read_text(encoding="utf-8", errors="replace")
    messages: List[ChatMessage] = []
    for block in iter_default_message_blocks(text):
        from_m = _FROM_RE.search(block)
        text_m = _TEXT_RE.search(block)
        if not from_m or not text_m:
            continue
        from_name = _clean_html_text(from_m.group(1))
        msg_text = _clean_html_text(text_m.group(1))
        if msg_text == "":
            continue
        date_title_m = _DATE_TITLE_RE.search(block)
        date_title = date_title_m.group(1) if date_title_m else None
        messages.append(ChatMessage(from_name=from_name.strip(), text=msg_text, date_title=date_title))
    return messages


def extract_added_employees(messages: List[ChatMessage], bot_name: Optional[str] = None) -> List[dict]:
    """
    Extract employees added via the bot flow:
    bot: PROMPT_USER_ID -> admin: <digits> -> bot: PROMPT_FULL_NAME -> admin: <full name>
    """
    # Auto-detect bot name if not provided: the sender who emits both prompts.
    if bot_name is None:
        candidates = {}
        for m in messages:
            if m.text in (PROMPT_USER_ID, PROMPT_FULL_NAME):
                candidates[m.from_name] = candidates.get(m.from_name, 0) + 1
        bot_name = max(candidates, key=candidates.get) if candidates else None

    out: List[dict] = []
    state = "idle"
    pending_user_id: Optional[int] = None
    pending_meta: dict = {}

    def is_bot(msg: ChatMessage) -> bool:
        return bot_name is not None and msg.from_name.strip() == bot_name.strip()

    for msg in messages:
        if state == "idle":
            if is_bot(msg) and msg.text == PROMPT_USER_ID:
                state = "await_user_id"
                pending_user_id = None
                pending_meta = {"added_at": msg.parsed_dt or msg.date_title, "source_prompt": PROMPT_USER_ID}
        elif state == "await_user_id":
            # next non-bot text should be user id
            if is_bot(msg):
                continue
            uid_txt = msg.text.strip()
            if re.fullmatch(r"\d{4,15}", uid_txt):
                pending_user_id = int(uid_txt)
                pending_meta["added_by"] = msg.from_name
                pending_meta["user_id_message_at"] = msg.parsed_dt or msg.date_title
                state = "await_full_name_prompt"
            else:
                # aborted / unexpected; reset
                state = "idle"
                pending_user_id = None
                pending_meta = {}
        elif state == "await_full_name_prompt":
            if is_bot(msg) and msg.text == PROMPT_FULL_NAME:
                pending_meta["full_name_prompt_at"] = msg.parsed_dt or msg.date_title
                state = "await_full_name"
            elif not is_bot(msg):
                # if admin sends something else before prompt, treat as abort
                state = "idle"
                pending_user_id = None
                pending_meta = {}
        elif state == "await_full_name":
            if is_bot(msg):
                continue
            full_name = msg.text.strip()
            if pending_user_id is None or full_name == "":
                state = "idle"
                pending_user_id = None
                pending_meta = {}
                continue
            out.append(
                {
                    "user_id": pending_user_id,
                    "name": full_name,
                    **pending_meta,
                }
            )
            state = "idle"
            pending_user_id = None
            pending_meta = {}

    return out


def _load_all_messages(input_paths: List[Path]) -> List[ChatMessage]:
    all_msgs: List[ChatMessage] = []
    for p in input_paths:
        all_msgs.extend(parse_messages_from_html_file(p))
    return all_msgs


def _sorted_html_files_from_dir(dir_path: Path) -> List[Path]:
    html_files = sorted(dir_path.glob("*.html"))
    # Telegram exports often paginate as messages.html, messages2.html, messages3.html...
    # Sorting by filename keeps chronological order for this export format.
    return html_files


def main() -> None:
    ap = argparse.ArgumentParser(description="Parse Telegram HTML export and extract employees added via bot flow.")
    ap.add_argument("--input-dir", type=str, help="Directory containing messages*.html (Telegram export)")
    ap.add_argument("--input", action="append", default=[], help="Explicit HTML file path(s). Can be repeated.")
    ap.add_argument("--output", type=str, required=True, help="Output JSON path")
    ap.add_argument("--bot-name", type=str, default=None, help="Bot sender name in export (optional, auto-detected)")
    ap.add_argument("--dedupe", action="store_true", help="Dedupe by user_id (keep last by appearance order)")
    args = ap.parse_args()

    inputs: List[Path] = []
    if args.input_dir:
        inputs.extend(_sorted_html_files_from_dir(Path(args.input_dir)))
    inputs.extend([Path(p) for p in args.input])
    # Remove duplicates while preserving order
    seen = set()
    uniq_inputs: List[Path] = []
    for p in inputs:
        rp = str(p.resolve())
        if rp in seen:
            continue
        seen.add(rp)
        uniq_inputs.append(p)
    if not uniq_inputs:
        raise SystemExit("No input HTML files provided/found.")

    messages = _load_all_messages(uniq_inputs)
    events = extract_added_employees(messages, bot_name=args.bot_name)

    data_out = {"source_files": [str(p) for p in uniq_inputs], "count": len(events), "employees": events}

    if args.dedupe:
        by_uid = {}
        for e in events:
            by_uid[int(e["user_id"])] = e
        deduped = list(by_uid.values())
        data_out["deduped_count"] = len(deduped)
        data_out["deduped_employees"] = deduped

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data_out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

