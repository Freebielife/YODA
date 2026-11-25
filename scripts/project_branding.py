"""Separate the official hero logo, explicitly chosen section flag and channel."""
import base64
import io
import json
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen


class BrandingError(ValueError):
    pass


def https_url(value):
    if not isinstance(value, str):
        raise BrandingError("Expected an HTTPS source URL")
    url = urlsplit(value)
    if url.scheme != "https" or not url.hostname or url.username or url.password or any(c.isspace() for c in value):
        raise BrandingError("Expected a public HTTPS source URL")
    return value


def channel_url(value):
    https_url(value)
    url = urlsplit(value)
    if url.hostname not in ("t.me", "telegram.me") or url.query or url.fragment or not re.fullmatch(r"/(?:[A-Za-z0-9_]+|\+[A-Za-z0-9_-]+)", url.path.rstrip('/')):
        raise BrandingError("Provide the token project's Telegram channel URL (https://t.me/channel)")
    return value


def validate_config(cfg, base, atlas_path):
    """Block incomplete branding before generating an apparently ready site."""
    if not cfg.get("logo_file") or cfg.get("logo_origin") not in ("token_metadata", "project_website"):
        raise BrandingError("Hero logo required: use token metadata or the project website, with logo_file and logo_origin")
    https_url(cfg.get("logo_source"))
    if not cfg.get("links", {}).get("telegram"):
        raise BrandingError("Project channel missing: ask the user for the Telegram channel")
    channel_url(cfg["links"]["telegram"])
    choices = [k for k in ("flag_catalog_key", "flag_file", "flag_emoji") if cfg.get(k)]
    if len(choices) != 1:
        raise BrandingError("Confirm one section flag from the catalogue; if absent, ask the user to provide its emoji/image")
    if cfg.get("flag_catalog_key"):
        atlas = json.loads(Path(atlas_path).read_text())
        if cfg["flag_catalog_key"] not in atlas["positions"]:
            raise BrandingError("Selected flag is unavailable in the bundled catalogue; ask the user for its emoji/image")
        cfg["flag_source"] = atlas.get("sources", {}).get(cfg["flag_catalog_key"], "Owner-approved catalogue")
    elif cfg.get("flag_emoji"):
        emoji = cfg["flag_emoji"]
        if not isinstance(emoji, str) or not 1 <= len(emoji) <= 16 or any(c in emoji for c in '<>\r\n') or emoji.isascii():
            raise BrandingError("Provide a short Unicode emoji or a local image for a custom Telegram emoji")
        if (not any(unicodedata.category(c) in ("So", "Sk") or c == "\u20e3" for c in emoji)
                or any(c.isspace() or (c.isalnum() and not (c.isdigit() and "\u20e3" in emoji)) for c in emoji)):
            raise BrandingError("Use an emoji, not a text label")
        cfg["flag_source"] = "Explicitly selected Unicode emoji"
    else:
        file = Path(cfg["flag_file"])
        if file.is_absolute() or ".." in file.parts or file.suffix.lower() not in (".webp", ".gif"):
            raise BrandingError("Flag must be a relative WebP/GIF emoji image")
        path = (base / file).resolve()
        if not path.is_relative_to(base.resolve()) or not path.is_file() or not 0 < path.stat().st_size <= 150000:
            raise BrandingError("Flag file is missing or exceeds 150 KB")
        from PIL import Image
        with Image.open(path) as img:
            if img.format not in ("WEBP", "GIF") or max(img.size) > 1024:
                raise BrandingError("Invalid flag image")
            img.verify()
        cfg["_flag"] = path
        cfg["flag_source"] = cfg.get("flag_source", "User-provided project emoji")


def install(output, cfg, atlas_path):
    """Embed the selected flag once and keep it out of the hero logo slot."""
    import shutil
    web = output / "web"
    if cfg.get("_flag"):
        path = cfg["_flag"]
        target = web / ("project-flag" + path.suffix.lower())
        shutil.copy2(path, target)
        mime = "image/gif" if target.suffix == ".gif" else "image/webp"
        flag = "data:" + mime + ";base64," + base64.b64encode(target.read_bytes()).decode()
    elif cfg.get("flag_catalog_key"):
        from PIL import Image
        atlas = json.loads(Path(atlas_path).read_text())
        x, y = atlas["positions"][cfg["flag_catalog_key"]]
        size = atlas["cell_size"]
        with Image.open(io.BytesIO(base64.b64decode(atlas["image_base64"]))) as img:
            crop = img.crop((x*size, y*size, (x+1)*size, (y+1)*size))
        target = web / "project-flag.webp"
        crop.save(target, "WEBP", quality=92)
        flag = "data:image/webp;base64," + base64.b64encode(target.read_bytes()).decode()
    else:
        flag = None
    if flag:
        css = (web / "telegram-taste.css").read_text().replace('background:var(--project-art) center/contain no-repeat!important;', 'background:var(--project-flag) center/contain no-repeat!important;')
        css += '\n:root{--project-flag:url("'+flag+'")}\n'
        (web / "telegram-taste.css").write_text(css)
    else:
        css = (web / "telegram-taste.css").read_text()
        css += '\n.brandGlyph.brand-project{background:transparent!important;color:inherit!important;font-size:18px!important;display:inline-flex;align-items:center;justify-content:center;overflow:hidden}\n'
        (web / "telegram-taste.css").write_text(css)
        app = web / "app.js"
        text = app.read_text().replace('function brandMarkNode(kind){', 'function brandMarkNode(kind){\n if(kind==="project"){const node=el("span",'+json.dumps(cfg['flag_emoji'])+',"brandGlyph brand-project");node.setAttribute("aria-hidden","true");return node;}')
        app.write_text(text)
    page = web / "page.html"
    page.write_text(page.read_text().replace('>Telegram</a>', '>Канал проекта</a>'))
    # Channel wording follows the selected interface language in both locations.
    value = page.read_text().replace('>Канал проекта</a>', ' data-t="projectChannel">Канал проекта</a>')
    page.write_text(value)
    app = web / "app.js"
    text = app.read_text().replace('const $=id=>', 'texts.ru.projectChannel="Канал проекта";texts.en.projectChannel="Project channel";\nconst $=id=>', 1)
    app.write_text(text)
    builder = output / "build.py"
    code, count = re.subn(r'else:\n    art = [^\n]+',
        'else:\n    raise ValueError("Official hero logo missing; restore it from metadata or project website")',
        builder.read_text(), count=1)
    if count != 1:
        raise BrandingError("Factory hero logo slot changed; review the integration")
    builder.write_text(code)
    project = output / "project.json"
    saved = json.loads(project.read_text())
    saved["branding"] = {"hero": {"origin": cfg["logo_origin"], "source": cfg["logo_source"], "file": "web/project-logo.webp"},
                         "sectionFlag": {"source": cfg["flag_source"], "catalogueKey": cfg.get("flag_catalog_key"), "emoji": cfg.get("flag_emoji")},
                         "channel": cfg["links"]["telegram"]}
    if flag:
        saved["branding"]["sectionFlag"]["file"] = "web/"+target.name
        if saved.get("flag_file"):
            saved["flag_file"] = "web/"+target.name
    project.write_text(json.dumps(saved, ensure_ascii=False, indent=2))


class WebsiteBranding(HTMLParser):
    def __init__(self, base):
        super().__init__()
        self.base, self.logos, self.channels = base, [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and any(key in attrs.get("rel", "").split() for key in ("icon", "apple-touch-icon")) and attrs.get("href"):
            self.logos.append(urljoin(self.base, attrs["href"]))
        if tag == "img" and attrs.get("itemprop") == "logo" and attrs.get("src"):
            self.logos.insert(0, urljoin(self.base, attrs["src"]))
        if tag == "a" and attrs.get("href"):
            candidate = urljoin(self.base, attrs["href"])
            try:
                self.channels.append(channel_url(candidate))
            except BrandingError:
                pass


def download(url, *, max_bytes=3_000_000):
    https_url(url)
    request = Request(url, headers={"User-Agent":"TON-Observatory/1.1", "Accept":"*/*"})
    with urlopen(request, timeout=20) as response:
        https_url(response.url)
        data = response.read(max_bytes+1)
        if len(data) > max_bytes:
            raise BrandingError("Branding resource exceeds size limit")
        return data


def prepare(cfg, directory, *, metadata_image=None, website=None, channel=None, flag_key=None, flag_file=None, flag_emoji=None, read=download):
    """Resolve branding during setup, then embed local verified raster assets."""
    from PIL import Image
    candidates = [(metadata_image, "token_metadata")] if metadata_image else []
    parser = None
    if website:
        https_url(website)
        parser = WebsiteBranding(website)
        try:
            parser.feed(read(website).decode("utf-8", errors="replace"))
        except OSError:
            parser = None
        if parser:
            candidates += [(url, "project_website") for url in parser.logos[:3]]
        cfg.setdefault("links", {})["website"] = website
    if not channel and parser and len(set(parser.channels)) == 1:
        channel = parser.channels[0]
    if not channel:
        raise BrandingError("Project channel missing: ask the user for the Telegram channel (--channel)")
    cfg.setdefault("links", {})["telegram"] = channel_url(channel)
    if flag_key: cfg["flag_catalog_key"] = flag_key
    elif flag_emoji: cfg["flag_emoji"] = flag_emoji
    elif flag_file:
        import shutil
        original = Path(flag_file).resolve()
        target = directory / ("selected-flag" + original.suffix.lower())
        shutil.copy2(original, target)
        cfg["flag_file"] = target.name
    else:
        raise BrandingError("Confirm a catalogue flag or ask the user to provide its emoji/image")
    for url, origin in candidates:
        try:
            raw = read(url)
            with Image.open(io.BytesIO(raw)) as image:
                if image.width * image.height > 16_000_000:
                    raise BrandingError("Logo dimensions exceed the setup budget")
                image.seek(0)
                image = image.convert("RGBA")
                image.thumbnail((256,256))
                image.save(directory / "hero-logo.webp", "WEBP", quality=90)
            cfg.update(logo_file="hero-logo.webp", logo_origin=origin, logo_source=url)
            return cfg
        except (OSError, ValueError, TypeError):
            continue
    raise BrandingError("Could not load the token logo from metadata or project website; provide a working official website/logo source")
