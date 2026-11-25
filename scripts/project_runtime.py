"""Shared release metadata, identity checks and atomic standalone publishing."""
import base64
import binascii
import json
import os
import re
from pathlib import Path

VERSION = "1.3.0"
DEFAULT_MAX_HTML_BYTES = 2_500_000


def canonical_address(value):
    if re.fullmatch(r"0:[0-9a-fA-F]{64}", str(value)):
        return value.lower()
    if not isinstance(value, str) or len(value) != 48:
        raise ValueError("Invalid mainnet TON address")
    try:
        data = base64.urlsafe_b64decode(value)
    except (ValueError, binascii.Error) as exc:
        raise ValueError("Invalid address encoding") from exc
    if (len(data) != 36 or data[0] not in (0x11, 0x51) or data[1] != 0 or
            binascii.crc_hqx(data[:34], 0) != int.from_bytes(data[34:], "big")):
        raise ValueError("Invalid mainnet basechain address or CRC")
    return "0:" + data[2:34].hex()


def read_project(root):
    project = json.loads((Path(root) / "project.json").read_text())
    canonical_address(project["master"])
    return project


def check_identity(snapshot, project):
    if snapshot.get("schema") != 1 or canonical_address(snapshot.get("token")) != canonical_address(project["master"]):
        raise ValueError("Snapshot belongs to a different token or schema")
    configured = {canonical_address(p["address"]) for p in project["pools"]}
    for row in snapshot.get("trades", {}).get("rows", []):
        if canonical_address(row.get("pool")) not in configured:
            raise ValueError("Trade belongs to an unconfigured pool")


def publish_html(root, result, snapshot):
    root = Path(root)
    project = read_project(root)
    check_identity(snapshot, project)
    if project.get("engine_version") == VERSION:
        branding = project.get("branding", {})
        if not all(branding.get(key) for key in ("hero", "sectionFlag", "channel")):
            raise ValueError("Official logo, confirmed section flag and project channel are required")
        if (branding["channel"] != project.get("links", {}).get("telegram") or
                branding["hero"]["source"] != project.get("logo_source") or
                branding["hero"]["origin"] != project.get("logo_origin")):
            raise ValueError("Branding configuration changed; regenerate the project")
        if not (root / branding["hero"]["file"]).is_file():
            raise ValueError("Official hero logo file missing")
    size = len(result.encode("utf-8"))
    limit = project.get("max_html_bytes", DEFAULT_MAX_HTML_BYTES)
    if type(limit) is not int or not 250_000 <= limit <= 5_000_000:
        raise ValueError("Invalid HTML size budget")
    report = {"engineVersion": VERSION, "htmlBytes": size, "limitBytes": limit,
              "snapshotBytes": len(json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")).encode()),
              "imageDataBytes": sum(len(x.encode()) for x in re.findall(r"data:image/[^\s\"'<>]+", result)),
              "webSourceBytes": {p.name: p.stat().st_size for p in (root / "web").iterdir() if p.is_file()}}
    print(json.dumps(report, ensure_ascii=False))
    if size > limit:
        raise ValueError(f"HTML size {size} exceeds {limit}; last good index.html retained")
    if re.search(r'<(?:script|img|link)\b[^>]*(?:src|href)\s*=\s*[\"\']https?://', result, re.I):
        raise ValueError("External rendering dependency in standalone HTML")
    if re.search(r'url\(\s*[\"\']?https?://', result, re.I):
        raise ValueError("External CSS rendering dependency")
    temporary = root / "index.html.tmp"
    temporary.write_text(result, encoding="utf-8")
    os.replace(temporary, root / "index.html")
    (root / "build").mkdir(exist_ok=True)
    (root / "build/report.json").write_text(json.dumps(report, indent=2))


def decorate_snapshot(snapshot, project):
    """Attach provenance without asserting unnamed contracts belong to a service."""
    snapshot["engineVersion"] = VERSION
    snapshot["methodology"] = project.get("methodology", {})
    manual = {canonical_address(w): label for w, label in project.get("services", {}).items()}
    pool_addresses = {canonical_address(p["address"]) for p in project["pools"]}
    for wallet, record in snapshot.get("identity", {}).get("byWallet", {}).items():
        role = record.get("role")
        if not role:
            continue
        if wallet in manual:
            proof = project.get("service_provenance", {}).get(wallet, {})
            record.update(serviceCategory=proof.get("category", "service"),
                          roleSource=proof.get("source", "project.json (project attribution)"))
        elif record.get("roleRegistry"):
            record["serviceCategory"] = "custody"
        else:
            category = "contract"
            if wallet in pool_addresses or role in ("DeDust Pool", "STON.fi Pool V1", "STON.fi Pool V2"):
                category = "pool"
            elif role in ("STON.fi Router V1", "STON.fi Router V2"):
                category = "router"
            elif role == "DeDust Vault":
                category = "vault"
            record.update(serviceCategory=category, roleSource="https://tonapi.io/v2/accounts/" + wallet)
