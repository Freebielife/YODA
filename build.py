"""Bundle a configured, independent observatory into one HTML file."""
import base64
import json
from pathlib import Path
from scripts.icon_pack import embedded_script
from scripts.project_runtime import publish_html

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
template = (WEB / "page.html").read_text()
for marker, filename in (
    ("/*LOADER*/", "snapshot-loader.js"),
    ("/*MARKET_CAP*/", "market-cap.js"),
    ("/*STYLE*/", "style.css"),
    ("/*APP*/", "app.js"),
):
    content = (WEB / filename).read_text()
    if filename == "style.css":
        content += "\n" + (WEB / "telegram-taste.css").read_text()
    template = template.replace(marker, content)
template = template.replace("/*ICONS*/", embedded_script())
if (WEB / "project-logo.webp").exists():
    art = "data:image/webp;base64," + base64.b64encode((WEB / "project-logo.webp").read_bytes()).decode("ascii")
else:
    raise ValueError("Official hero logo missing; restore it from metadata or project website")
background = "data:image/svg+xml;base64," + base64.b64encode(
    b'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120">'
    b'<rect width="120" height="120" fill="#090e18"/>'
    b'<path d="M0 0L120 120M120 0L0 120" stroke="#25415a" stroke-opacity=".3"/>'
    b'</svg>').decode("ascii")
if (WEB / "project-background.webp").exists():
    background = "data:image/webp;base64," + base64.b64encode(
        (WEB / "project-background.webp").read_bytes()).decode("ascii")
template = template.replace("__PROJECT_ART__", art).replace("__PROJECT_BG__", background)
snapshot = json.loads((ROOT / "data/snapshot.json").read_text())
payload = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
result = template.replace("__SNAPSHOT__", payload)
if any(x in result for x in ("/*APP*/", "/*STYLE*/", "/*LOADER*/", "/*MARKET_CAP*/",
                             "__PROJECT_ART__", "__PROJECT_BG__", "__BADGE_")):
    raise ValueError("Unresolved template marker")
publish_html(ROOT, result, snapshot)
