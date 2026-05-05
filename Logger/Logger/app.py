from html import escape
from pathlib import Path

from flask import Flask, request

app = Flask(__name__)
LOG_FILE = Path("visits.log")


def get_visitor_ip() -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "unknown"


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


def render_remove_page(visitor_ip: str, removed_count: int | None = None) -> str:
    visitor_ip_html = escape(visitor_ip)

    result_html = ""
    if removed_count is not None:
        result_html = (
            f"<p class='meta'>Removed <strong>{removed_count}</strong> matching "
            f"log entr{'y' if removed_count == 1 else 'ies'} for this IP.</p>"
        )

    return f"""
    <html>
      <head>
        <title>Remove IP</title>
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
            background: #dc2626;
            color: white;
            border: 0;
            border-radius: 10px;
            padding: 12px 18px;
            cursor: pointer;
            font-size: 15px;
          }}
          button:hover {{
            background: #b91c1c;
          }}
          .meta {{
            color: #cbd5e1;
          }}
        </style>
      </head>
      <body>
        <div class="card">
          <h1>Remove IP</h1>
          <p>Detected IP: <code>{visitor_ip_html}</code></p>
          <p>Press the button below to remove matching entries for this IP from <code>visits.log</code>.</p>
            </form>
          </div>
        </div>
      </body>
    </html>
    """


@app.route("/")
def home():
    visitor_ip = get_visitor_ip()
    return render_remove_page(visitor_ip)


@app.post("/remove")
def remove_ip():
    visitor_ip = get_visitor_ip()
    removed_count = remove_ip_entries(visitor_ip)
    return render_remove_page(visitor_ip, removed_count=removed_count)


if __name__ == "__main__":
    print("Remove IP page running.")
    print("Open http://127.0.0.1:5000 or your LAN/tunnel URL.")
    app.run(host="0.0.0.0", port=5000)
