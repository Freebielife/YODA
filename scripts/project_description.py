"""Source-attributed README descriptions; metadata remains a project's own claim."""
from datetime import date, datetime, timezone
import html
import re
from urllib.parse import urlsplit


def validate(description):
    if description is None:
        return
    if not isinstance(description, dict):
        raise ValueError("project_description must be an object")
    text = description.get("text")
    if not isinstance(text, str) or not 1 <= len(text.strip()) <= 2000:
        raise ValueError("project_description.text must contain 1..2000 characters")
    if description.get("origin") not in ("token_metadata", "reviewed_sources"):
        raise ValueError("Description origin must be token_metadata or reviewed_sources")
    try:
        date.fromisoformat(description["checked_at"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Description checked_at must be an ISO date") from error
    sources = description.get("sources")
    if not isinstance(sources, list) or not 1 <= len(sources) <= 10:
        raise ValueError("Description needs 1..10 source URLs")
    for source in sources:
        if not isinstance(source, str) or re.search(r'[\s<>"\\]', source):
            raise ValueError("Invalid description source URL")
        parsed = urlsplit(source)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Description sources must be public HTTPS URLs")


def from_metadata(metadata, source):
    text = metadata.get("description")
    if not isinstance(text, str):
        return None
    text = " ".join(text.split())
    # Contract addresses and bare URLs are not narrative descriptions.
    if (not text or len(text) > 2000 or
            re.fullmatch(r"(?:0x)?[0-9a-fA-F]{40,64}|0:[0-9a-fA-F]{64}|https?://\S+", text)):
        return None
    result = {"text": text, "origin": "token_metadata", "sources": [source],
              "checked_at": datetime.now(timezone.utc).date().isoformat()}
    validate(result)
    return result


def section(description):
    validate(description)
    if description is None:
        return ("## О проекте / токене\n\n"
                "Описание пока не подтверждено. Перед публикацией добавьте описание, "
                "первичные источники и дату проверки в project_description в project.json.\n\n")
    # Render untrusted project text as plain text, never as active Markdown/HTML.
    text = html.escape(" ".join(description["text"].split()), quote=False)
    text = re.sub(r"([\\`*_{}\[\]()!|])", r"\\\1", text)
    origin = ("Самоописание из метаданных токена; заявления проекта не проверены независимо."
              if description["origin"] == "token_metadata" else
              "Краткое описание по указанным первичным источникам.")
    sources = "\n".join("- <" + url + ">" for url in description["sources"])
    return ("## О проекте / токене\n\n" + text + "\n\n" + origin +
            "\n\nИсточники (проверены " + description["checked_at"] + "):\n\n" + sources + "\n\n")
