import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def api_url(token: str, method: str) -> str:
    return f"https://api.telegram.org/bot{token}/{method}"


def request_json(url: str, data: dict) -> dict:
    payload = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram API error {e.code}: {body}") from e


def main() -> int:
    token = os.getenv("BOT_TOKEN", "").strip()
    webhook_url = os.getenv("WEBHOOK_URL", "").strip()
    drop_pending = os.getenv("WEBHOOK_DROP_PENDING_UPDATES", "true").lower() in {"1", "true", "yes"}

    if not token:
        print("BOT_TOKEN is required", file=sys.stderr)
        return 2
    if not webhook_url:
        print("WEBHOOK_URL is required (set PUBLIC_BASE_URL in .env)", file=sys.stderr)
        return 2

    r = request_json(
        api_url(token, "setWebhook"),
        {
            "url": webhook_url,
            "drop_pending_updates": "true" if drop_pending else "false",
        },
    )
    ok = bool(r.get("ok"))
    if not ok:
        print(json.dumps(r, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(json.dumps(r, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

