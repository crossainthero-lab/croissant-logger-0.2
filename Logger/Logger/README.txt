IP LOGGER WITH CONSENT

What this does:
- Runs a tiny web server on your Windows PC.
- Logs local/private visitors immediately.
- Shows a simple notice page before logging remote/public visitors.
- Lets visitors remove their own IP entries with a visible Remove IP button.
- Can expose the app remotely through a Cloudflare tunnel when cloudflared is installed.

How to run:
1. Extract this ZIP.
2. Double-click run.bat.
3. If cloudflared is installed, run.bat will also open a public tunnel for remote access.
4. When the tunnel URL appears, run.bat copies it to your clipboard automatically.
5. If cloudflared is not installed, local access still works and the launcher will tell you what is missing.
6. For local testing on Windows, open Command Prompt and type:
   ipconfig
7. Find your IPv4 Address, usually like:
   192.168.1.23
8. On another device on the same Wi-Fi, open:
   http://192.168.1.23:5000
9. For remote access, paste or share the Cloudflare tunnel URL from your clipboard.

Logs:
- Visits are saved in visits.log beside app.py.

Notes:
- Remote/public visitors are shown a notice page with a `Continue and log my IP` button before anything is logged.
- After consenting, visitors can still remove their IP entries using the Remove IP button.
- run.bat creates a temporary FLASK_SECRET_KEY automatically for each launch.
- You can still use port forwarding or another tunnel if you prefer, but Cloudflare is the fastest path.
