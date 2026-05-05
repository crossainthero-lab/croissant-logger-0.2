import os
from datetime import datetime
from html import escape
from ipaddress import ip_address
from pathlib import Path

from flask import Flask, request, session

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-secret-before-sharing")
LOG_FILE = Path("visits.log")


def is_private_or_local(ip: str) -> bool:
    try:
        addr = ip_address(ip.split(",")[0].strip())
        return addr.is_private or addr.is_loopback
    except ValueError:
        return False


def get_visitor_ip() -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "unknown"


def append_log(visitor_ip: str, user_agent: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    scope = "Local IP" if is_private_or_local(visitor_ip) else "Remote IP"
    line = f"[{timestamp}] {scope}: {visitor_ip} | User-Agent: {user_agent}"
    print(line)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def remove_ip_entries(visitor_ip: str) -> int:
    if not LOG_FILE.exists():
        return 0

    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    kept_lines = []
    removed_count = 0

    for line in lines:
        if f": {visitor_ip} |" in line:
            removed_count += 1
            continue
        kept_lines.append(line)

    text = "\n".join(kept_lines)
    if kept_lines:
        text += "\n"
    LOG_FILE.write_text(text, encoding="utf-8")
    return removed_count


def render_page(
    visitor_ip: str,
    message: str,
    removed_count: int | None = None,
    title: str = "Your IP has been logged",
) -> str:
    visitor_ip_html = escape(visitor_ip)
    message_html = escape(message)
    title_html = escape(title)
    removed_html = ""

    if removed_count is not None:
        removed_html = (
            f"<p class='meta'>Removed <strong>{removed_count}</strong> matching "
            f"log entr{'y' if removed_count == 1 else 'ies'} for this IP.</p>"
        )

    return f"""
    <html>
      <head>
        <title>IP Logger</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: #e5e7eb;
            padding: 40px;
          }}
          .card {{
            background: #111827;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 24px;
            max-width: 720px;
          }}
          h1 {{
            margin-top: 0;
          }}
          code {{
            background: #020617;
            padding: 4px 8px;
            border-radius: 6px;
          }}
          .actions {{
            margin-top: 24px;
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
          }}
          button {{
            border: 0;
            border-radius: 10px;
            padding: 12px 18px;
            cursor: pointer;
            font-size: 15px;
          }}
          .danger {{
            background: #dc2626;
            color: white;
          }}
          .danger:hover {{
            background: #b91c1c;
          }}
          .primary {{
            background: #2563eb;
            color: white;
          }}
          .primary:hover {{
            background: #1d4ed8;
          }}
          .meta {{
            color: #cbd5e1;
          }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>{title_html}</h1>
          <p>{message_html}</p>
          <p>Detected IP: <code>{visitor_ip_html}</code></p>
          <p>User-Agent details are stored in <code>visits.log</code>.</p>
          {removed_html}
          <div class="actions">
            <form method="post" action="/remove">
              <button class="danger" type="submit">Remove IP</button>
            </form>
          </div>
        </div>
      </body>
    </html>
    """


def render_notice_page(visitor_ip: str) -> str:
    visitor_ip_html = escape(visitor_ip)
    return f"""
    <html>
      <head>
        <title>Notice Before Logging</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background: #0f172a;
            color: #e5e7eb;
            padding: 40px;
          }}
          .card {{
            background: #111827;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 24px;
            max-width: 720px;
          }}
          h1 {{
            margin-top: 0;
          }}
          code {{
            background: #020617;
            padding: 4px 8px;
            border-radius: 6px;
          }}
          .actions {{
            margin-top: 24px;
          }}
          button {{
            background: #2563eb;
            color: white;
            border: 0;
            border-radius: 10px;
            padding: 12px 18px;
            cursor: pointer;
            font-size: 15px;
          }}
          button:hover {{
            background: #1d4ed8;
          }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Notice Before Logging</h1>
          <p>You are accessing this page from outside the local/private network.</p>
          <p>If you continue, this page will log your IP address and User-Agent to <code>visits.log</code>.</p>
          <p>Detected IP: <code>{visitor_ip_html}</code></p>
          <p>You can still remove your IP afterward using the visible <code>Remove IP</code> button.</p>
          <div class="actions">
            <form method="post" action="/consent">
              <button type="submit" name="decision" value="agree">Continue and log my IP</button>
            </form>
          </div>
        </div>
      </body>
    </html>
    """


@app.route("/")
def home():
    visitor_ip = get_visitor_ip()

    if is_private_or_local(visitor_ip):
        user_agent = request.headers.get("User-Agent", "unknown")
        append_log(visitor_ip, user_agent)
        return render_page(visitor_ip, "This visit was logged when the page loaded.")

    if session.get("consented_ip") == visitor_ip:
        return render_page(
            visitor_ip,
            "This IP has already been approved for logging during this browser session. Use Remove IP if you want to delete your entries.",
        )

    return render_notice_page(visitor_ip)


@app.post("/consent")
def consent():
    visitor_ip = get_visitor_ip()
    session["consented_ip"] = visitor_ip
    user_agent = request.headers.get("User-Agent", "unknown")
    append_log(visitor_ip, user_agent)
    return render_page(
        visitor_ip,
        "Your IP has now been logged. You can remove it below at any time.",
    )


@app.post("/remove")
def remove_ip():
    visitor_ip = get_visitor_ip()
    removed_count = remove_ip_entries(visitor_ip)
    if session.get("consented_ip") == visitor_ip:
        session.pop("consented_ip", None)
    return render_page(
        visitor_ip,
        "Your request to remove this IP from the log has been processed.",
        removed_count=removed_count,
        title="IP Removal Complete",
    )


if __name__ == "__main__":
    print("IP Logger running.")
    print("Local/private visitors are logged immediately.")
    print("Remote/public visitors must continue from the notice page before logging.")
    print("Expose port 5000 with a tunnel if you want remote access.")
    app.run(host="0.0.0.0", port=5000)
