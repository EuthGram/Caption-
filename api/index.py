"""
EuthCap - Homepage
-------------------
Serves a premium dark-UI status page at the root of the deployment.
Purely informational, no external calls, no database.

Developer: Euthle
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# Static build metadata shown on the homepage.
BOT_NAME = "EuthCap"
BOT_VERSION = "1.0"
PYTHON_VERSION = "3.12"
DEVELOPER = "Euthle"

HTML_PAGE = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{BOT_NAME} · TMDb Caption Bot</title>
<style>
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}

    body {{
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle at 20% 20%, #14141c 0%, #0a0a0f 55%, #050507 100%);
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #e8e8f0;
        padding: 24px;
    }}

    .card {{
        width: 100%;
        max-width: 420px;
        background: linear-gradient(160deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015));
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 40px 32px;
        backdrop-filter: blur(18px);
        box-shadow: 0 20px 60px rgba(0,0,0,0.55), inset 0 1px 0 rgba(255,255,255,0.04);
        text-align: center;
    }}

    .emoji {{
        font-size: 46px;
        margin-bottom: 6px;
        filter: drop-shadow(0 0 18px rgba(124,92,255,0.55));
    }}

    h1 {{
        font-size: 26px;
        font-weight: 700;
        letter-spacing: 0.5px;
        background: linear-gradient(90deg, #a78bfa, #67e8f9);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }}

    .tagline {{
        margin-top: 6px;
        font-size: 13px;
        color: #8b8b9c;
        letter-spacing: 0.3px;
    }}

    .divider {{
        height: 1px;
        margin: 26px 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.14), transparent);
    }}

    .stats {{
        display: flex;
        flex-direction: column;
        gap: 14px;
        text-align: left;
    }}

    .stat {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 14px;
        border-radius: 12px;
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.05);
        font-size: 13.5px;
    }}

    .stat .label {{
        color: #a7a7b8;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .stat .value {{
        font-weight: 600;
        color: #f1f1f8;
    }}

    .online {{
        color: #34d399;
    }}

    .online::before {{
        content: '';
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #34d399;
        margin-right: 6px;
        box-shadow: 0 0 10px #34d399;
    }}

    .footer {{
        margin-top: 28px;
        font-size: 12px;
        color: #5c5c6e;
        letter-spacing: 0.4px;
    }}

    .footer b {{
        color: #a78bfa;
    }}
</style>
</head>
<body>
    <div class="card">
        <div class="emoji">🎬</div>
        <h1>{BOT_NAME}</h1>
        <div class="tagline">Python Telegram TMDb Caption Bot</div>

        <div class="divider"></div>

        <div class="stats">
            <div class="stat">
                <span class="label">🟢 Status</span>
                <span class="value online">Online</span>
            </div>
            <div class="stat">
                <span class="label">⚡ Runtime</span>
                <span class="value">Vercel</span>
            </div>
            <div class="stat">
                <span class="label">🐍 Python</span>
                <span class="value">{PYTHON_VERSION}</span>
            </div>
            <div class="stat">
                <span class="label">🏷 Version</span>
                <span class="value">{BOT_VERSION}</span>
            </div>
            <div class="stat">
                <span class="label">👤 Developer</span>
                <span class="value">{DEVELOPER}</span>
            </div>
        </div>

        <div class="footer">Made By <b>{DEVELOPER}</b></div>
    </div>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
async def homepage() -> HTMLResponse:
    """Serve the premium dark-UI status page.

    Registered under both "/" and "/api/index" because Vercel's rewrite
    (source "/" -> destination "/api/index") passes the destination path
    through to the ASGI app, not the original "/".
    """
    return HTMLResponse(content=HTML_PAGE, status_code=200)
   
