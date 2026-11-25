"""Generate an isolated TON observatory from this repository's frozen source.

Fail-closed: only verified native TON pools, no copied Ludoman artwork,
NFT badges, locks, staking, external links or service wallet mappings.
"""
from __future__ import annotations

import argparse
import ast
import base64
import binascii
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote, urlsplit
from scripts.build_common_flags import build_common_atlas
from scripts.check_reference import check_reference
from scripts.foundation import install as install_foundation
from scripts.project_branding import validate_config as validate_branding, install as install_branding, BrandingError
from scripts.project_description import validate as validate_description, section as description_section

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "reference"


def source_file(relative):
    frozen = REFERENCE / relative
    return frozen if frozen.is_file() else ROOT / relative

DEXES = {"stonfi": ("STON.fi", "ston", "https://app.ston.fi"),
         "dedust": ("DeDust", "dedust", "https://dedust.io")}
CORE = ("scripts/project_runtime.py", "trade_history.py", "tests/test_trade_history.py", "service_registry.py", "common-services.json", "tests/test_service_registry.py", "assets.py", "trades.py", "pools.py", "collect.py", "domains.py",
        "verify.py", "web/app.js", "web/page.html", "web/style.css",
        "web/telegram-taste.css", "web/market-cap.js", "web/snapshot-loader.js",
        "scripts/icon_pack.py", "scripts/publish_snapshot.py",
        "scripts/refresh_observatory.py", "tests/test_refresh_sources.py",
        "tests/market-cap.test.cjs", "tests/snapshot-loader.test.cjs")
COMMON_SVGS = ("brands/telegram.svg", "brands/ton.svg", "brands/usdt.svg",
               "brands/github.svg", "brands/x.svg",
               "ui/arrow-left-right.svg", "ui/chart-no-axes-combined.svg",
               "ui/external-link.svg", "ui/list-filter.svg", "ui/lock.svg",
               "ui/search.svg", "ui/settings.svg", "ui/snowflake.svg",
               "ui/trophy.svg")


class ProjectError(ValueError):
    pass


def raw_address(address):
    """Decode TON-friendly basechain address with CRC-16 verification."""
    if not isinstance(address, str) or len(address) != 48:
        raise ProjectError("Expected a 48-character friendly TON address")
    try:
        data = base64.urlsafe_b64decode(address)
    except (ValueError, binascii.Error) as exc:
        raise ProjectError("Invalid TON address encoding") from exc
    if len(data) != 36 or (data[0] & 63) not in (0x11, 0x51):
        raise ProjectError("Invalid TON address tag")
    if binascii.crc_hqx(data[:34], 0) != int.from_bytes(data[34:], "big"):
        raise ProjectError("Invalid TON address checksum")
    chain = int.from_bytes(data[1:2], "big", signed=True)
    if chain != 0:
        raise ProjectError("Only TON basechain jettons are supported")
    return f"{chain}:{data[2:34].hex()}"


def require(data, key, typ=str):
    value = data.get(key)
    if not isinstance(value, typ) or (isinstance(value, str) and not value.strip()):
        raise ProjectError("Invalid or missing field: " + key)
    return value


def local_image(base, value, label, suffixes, max_bytes):
    """Use verified local raster files without external downloads or SVG scripts."""
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ProjectError(label + " must be a relative local image path")
    requested = Path(value)
    if ".." in requested.parts or requested.suffix.lower() not in suffixes:
        raise ProjectError(label + " has an unsupported path or image format")
    image = (base / requested).resolve()
    if not image.is_relative_to(base.resolve()) or not image.is_file():
        raise ProjectError(label + " must reference an existing local image")
    if not 0 < image.stat().st_size <= max_bytes:
        raise ProjectError(label + " is empty or exceeds its size limit")
    header = image.read_bytes()[:12]
    if requested.suffix.lower() == ".webp":
        valid = header.startswith(b"RIFF") and header[8:12] == b"WEBP"
    elif requested.suffix.lower() == ".gif":
        valid = header.startswith((b"GIF87a", b"GIF89a"))
    else:
        valid = False
    if not valid:
        raise ProjectError(label + " file content does not match its type")
    return image


def read_config(path):
    cfg = json.loads(path.read_text())
    try:
        validate_description(cfg.get("project_description"))
    except ValueError as error:
        raise ProjectError(str(error)) from error
    slug, symbol, name = (require(cfg, k) for k in ("slug", "symbol", "name"))
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,30}", slug):
        raise ProjectError("Invalid slug")
    if not re.fullmatch(r"[A-Z0-9_]{2,12}", symbol):
        raise ProjectError("Token symbol must use ASCII capitals, digits or underscores")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 -]{0,45}", name):
        raise ProjectError("Name may not contain markup")
    from scripts.project_runtime import canonical_address
    canonical_address(require(cfg, "master"))
    raw_address(cfg["master"])
    decimals = cfg.get("decimals")
    if type(decimals) is not int or not 0 <= decimals <= 18:
        raise ProjectError("Token decimals must be independently verified (0..18)")
    github = require(cfg, "github", dict)
    if not re.fullmatch(r"[A-Za-z0-9-]{1,39}", require(github, "owner")):
        raise ProjectError("Invalid GitHub owner")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", require(github, "repo")):
        raise ProjectError("Invalid repository name")
    pools = require(cfg, "pools", list)
    if not 1 <= len(pools) <= 20:
        raise ProjectError("One or more confirmed native TON pools are required")
    addresses = set()
    canonical_pools = set()
    for pool in pools:
        if not isinstance(pool, dict):
            raise ProjectError("Invalid pool definition")
        address = require(pool, "address")
        raw_address(address)
        normalized_pool = canonical_address(address)
        if normalized_pool in canonical_pools:
            raise ProjectError("Duplicate pool")
        canonical_pools.add(normalized_pool)
        addresses.add(address)
        if pool.get("dex") not in DEXES or pool.get("quote") != "TON":
            raise ProjectError("Only direct native TON pools on STON.fi or DeDust are supported")
        if "fee" in pool and not re.fullmatch(r"[0-9]+(?:\.[0-9]+)?%", str(pool["fee"])):
            raise ProjectError("Pool fee must be a verified percentage")
    if require(cfg, "primary_pool") not in addresses:
        raise ProjectError("Primary pool must be among the confirmed pool addresses")
    if cfg.get("quote", "TON") != "TON":
        raise ProjectError("Only native TON quote is supported by this collector")
    links = cfg.get("links", {})
    if not isinstance(links, dict) or set(links) - {"website", "telegram", "x", "staking"}:
        raise ProjectError("Unsupported link keys")
    for key, url in links.items():
        if not isinstance(url, str) or not re.fullmatch(r"https://[A-Za-z0-9.-]+(?::[0-9]+)?(?:/[^ \r\n\t<>]*)?", url):
            raise ProjectError("Invalid HTTPS link: " + key)
    services = cfg.get("services", {})
    if not isinstance(services, dict):
        raise ProjectError("services must be an address-to-name dictionary")
    shared_overrides = json.loads((ROOT / "service-overrides.json").read_text())
    shared_services = {address: item["name"] for address, item in shared_overrides.items()}
    cfg["services"] = {**shared_services, **services}
    cfg["service_provenance"] = {
        canonical_address(address): {"category": item["category"], "source": item["source"]}
        for address, item in shared_overrides.items() if address not in services}
    cfg["_services"] = {canonical_address(address): require({"name": title}, "name")
                        for address, title in cfg["services"].items()}
    if cfg.get("logo_file"):
        cfg["_logo"] = local_image(path.parent, cfg["logo_file"], "logo_file", {".webp"}, 150000)
    if cfg.get("background_file"):
        cfg["_background"] = local_image(
            path.parent, cfg["background_file"], "background_file", {".webp"}, 750000)
    badges = cfg.get("badges", [])
    if not isinstance(badges, list) or len(badges) > 12:
        raise ProjectError("badges must be an array of up to twelve custom badges")
    reserved = {"og", "digits", "fragmentNumber", "burner", "staking"}
    badge_icons, seen = {}, set()
    for badge in badges:
        if not isinstance(badge, dict):
            raise ProjectError("Each badge must be an object")
        key = require(badge, "id")
        if not re.fullmatch(r"[a-z][a-z0-9_]{1,23}", key) or key in seen or key in reserved:
            raise ProjectError("Badge ID must be unique and distinct from built-ins")
        seen.add(key)
        for label in ("label", "description_ru", "description_en"):
            val = require(badge, label)
            if not 1 <= len(val) <= (40 if label == "label" else 250):
                raise ProjectError("Invalid badge text length: " + label)
        color = badge.get("color")
        if color is not None and (not isinstance(color, str) or
                                  not re.fullmatch(r"#[0-9a-fA-F]{6}", color)):
            raise ProjectError("Badge color must be an RGB hex color")
        if "url" in badge:
            url = badge["url"]
            if not isinstance(url, str) or not re.fullmatch(
                r"https://[A-Za-z0-9.-]+(?::[0-9]+)?(?:/[^ \r\n\t<>]*)?", url):
                raise ProjectError("Badge URL must use HTTPS")
        if badge.get("icon_file"):
            badge_icons[key] = local_image(
                path.parent, badge["icon_file"], "badge icon " + key,
                {".webp", ".gif"}, 150000)
        if badge.get("match", "any") not in ("any", "all"):
            raise ProjectError("Badge match supports only 'any' or 'all'")
        criteria = require(badge, "criteria", list)
        if not 1 <= len(criteria) <= 3:
            raise ProjectError("Each badge needs 1–3 verifiable on-chain criteria")
        for rule in criteria:
            if not isinstance(rule, dict):
                raise ProjectError("Badge criterion must be an object")
            if rule.get("type") == "jetton_min":
                raw_address(require(rule, "master"))
                amount = rule.get("min_balance")
                if type(amount) is not int or not 0 < amount <= 10**15:
                    raise ProjectError("Jetton badge min_balance must be positive integer")
            elif rule.get("type") == "nft_collection":
                raw_address(require(rule, "collection"))
            else:
                raise ProjectError("Unsupported badge proof: use jetton_min or nft_collection")
    cfg["_badge_icons"] = badge_icons
    try:
        validate_branding(cfg, path.parent, ROOT / "assets/icon-pack/approved-brand-atlas.json")
    except BrandingError as error:
        raise ProjectError(str(error)) from error
    return cfg


def replace(source, old, new, label):
    if old not in source:
        raise ProjectError("Frozen factory reference changed: " + label)
    return source.replace(old, new)


def generic(source, cfg):
    return (source.replace("__LUDOMAN_ART__", "__PROJECT_ART__")
            .replace("__OBSERVATORY_BG__", "__PROJECT_BG__")
            .replace("LUDOMAN", cfg["symbol"])
            .replace("Ludoman", cfg["name"])
            .replace("ludoman", "project")
            .replace("GRAM", "TON"))


def schema(source):
    source = source.replace('"project":', '"tokenAmount":')
    source = source.replace('["project"]', '["tokenAmount"]')
    return re.sub(r"\.project\b", ".tokenAmount", source)


def helper(source, name):
    tree = ast.parse(source)
    node = next((x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == name), None)
    if node is None:
        raise ProjectError("Helper missing from reference: " + name)
    return "\n".join(source.splitlines()[node.lineno-1:node.end_lineno]) + "\n"


def common_badges(source, cfg):
    """Generic badge collectors with independently verifiable chain conditions."""
    methods = [helper(source, n) for n in
               ("raw_friendly", "decode_address", "fragment_number_owner",
                "refresh_fragment_numbers", "holders", "nft_owners")]
    rules = {
        entry["id"]: {"match": entry.get("match", "any"),
                      "criteria": entry["criteria"]}
        for entry in cfg.get("badges", [])
    }
    head = '''"""TON/DNS/Fragment and project-configured badge proofs. No foreign NFTs."""
import base64
import binascii
import re
import time
from assets import fetch, raw_address
from domains import pages, owned, check_queue

ZERO = "0:" + "0" * 64
FRAGMENT_NUMBERS = "0:0e41dc1dc3c9067ed24248580e12b3359818d83dee0304fabcf80845eafafdb2"
'''
    head += "\nBADGE_RULES = " + repr(rules) + "\n"
    head += '''
def refresh(previous, now):
    # Recheck expensive on-chain holder/NFT sources at most every six hours.
    # A failing source does not grant an unconfirmed badge.
    old = previous.get("sources", {})
    sources = {key: old[key] for key in BADGE_RULES if key in old}
    failed = []
    for key, spec in BADGE_RULES.items():
        last = sources.get(key, {})
        if last.get("asOf", 0) > now - 6 * 3600:
            continue
        try:
            sets = []
            for criterion in spec["criteria"]:
                if criterion["type"] == "jetton_min":
                    wallets = holders(criterion["master"], True, criterion["min_balance"])
                elif criterion["type"] == "nft_collection":
                    wallets = nft_owners(criterion["collection"], False)
                else:
                    raise ValueError("Unrecognized badge proof")
                sets.append(set(wallets))
            qualifying = (set.intersection(*sets) if spec["match"] == "all"
                          else set.union(*sets))
            sources[key] = {"asOf": now, "wallets": {wallet: True for wallet in qualifying}}
        except (OSError, ValueError, KeyError, RuntimeError) as error:
            failed.append(key)
            print("Badge source failed:", key, type(error).__name__, flush=True)
    return {"sources": sources, "failed": failed}
'''
    return head + "\n\n".join(methods)

def common_observatory(source, cfg):
    methods = [helper(source, n) for n in
               ("hash_hex", "to_zero", "zero_burns", "activation", "identity")]
    head = '''"""Zero-address burns and identified TON accounts. No staking assumptions."""
import base64
import time
import service_registry
from urllib.parse import urlencode
from assets import DOMAIN, MASTER, MASTER_RAW, fetch, raw_address, resolved_domain, token_amount
from domains import DIGITS
from badges import ZERO

TONCENTER = "https://toncenter.com/api/v3"
ROLES = {"dedust_vault":"DeDust Vault","stonfi_router_v2":"STON.fi Router V2",
         "stonfi_router_v1":"STON.fi Router V1","dedust_pool":"DeDust Pool",
         "stonfi_pool_v2":"STON.fi Pool V2","stonfi_pool_v1":"STON.fi Pool V1"}
RECOVERABLE = (OSError, ValueError, KeyError, RuntimeError)
'''
    head += "\nKNOWN_SERVICES = " + repr(cfg["_services"]) + "\n"
    head += '''def role(wallet, account, registry=None):
    if wallet in KNOWN_SERVICES:
        return KNOWN_SERVICES[wallet]
    custody = service_registry.lookup(wallet, registry)
    if custody:
        return custody
    known = next((ROLES[i] for i in account.get("interfaces", []) if i in ROLES), None)
    if known:
        return known
    # Generic contracts are not automatically a named service or human wallet.
    if account.get("status") == "active" and account.get("is_wallet") is False:
        return "unclassified_contract"
    return None
'''
    generated = schema(generic(head + "\n\n".join(methods), cfg))
    generated = generated.replace('start = max(1, previous.get("asOf", 1) - 3600)',
                                  'start = max(1, previous.get("asOf", now - 7 * 86400) - 3600)')
    return generated


def image_uri(path):
    suffix = path.suffix.lower()
    mime = "image/gif" if suffix == ".gif" else "image/webp"
    return "data:" + mime + ";base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def artwork(cfg):
    name = html.escape(cfg["symbol"][:3])
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">'
           '<defs><linearGradient id="g"><stop stop-color="#277cd2"/>'
           '<stop offset="1" stop-color="#142a4e"/></linearGradient></defs>'
           '<rect width="128" height="128" rx="32" fill="url(#g)"/>'
           '<text x="64" y="72" text-anchor="middle" font-size="36" '
           'font-family="system-ui" font-weight="800" fill="#e7f5ff">'
           + name + '</text></svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def page_html(source, cfg):
    symbol = html.escape(cfg["symbol"])
    telegram_button = (
        '<a href="' + html.escape(cfg["links"]["telegram"], quote=True) +
        '" target="_blank" rel="noopener noreferrer">Telegram</a>'
        if "telegram" in cfg.get("links", {}) else ""
    )
    source = replace(
        source,
        '<a href="https://t.me/the1000project" target="_blank" rel="noopener noreferrer">Telegram</a>',
        telegram_button, "remove Ludoman Telegram link from new hero")
    first = next(p for p in cfg["pools"] if p["address"] == cfg["primary_pool"])
    venue, venue_logo, _ = DEXES[first["dex"]]
    venues = list(dict.fromkeys(p["dex"] for p in cfg["pools"]))
    tag = ' / '.join('<span class="brandInline" data-brand="' + DEXES[dex][1] + '">' +
                     DEXES[dex][0] + '</span>' for dex in venues)
    cap = ('<div class="eyebrow marketChain"><span class="brandInline" data-brand="' +
           venue_logo + '">' + venue + '</span><span>/</span>' +
           '<span class="brandInline" data-brand="project">' + symbol + '</span> · ' +
           '<span class="brandInline" data-brand="ton">TON</span></div>')
    source, count = re.subn(r'<div class="eyebrow marketChain">.*?</div>',
                            lambda _: cap, source, count=1)
    if count != 1:
        raise ProjectError("Missing market brand heading")
    source, count = re.subn(r'<span class="tag dexTag">.*?</span></span>',
                            lambda _: '<span class="tag dexTag">' + tag + '</span>',
                            source, count=1)
    if count != 1:
        raise ProjectError("Missing operation-DEX heading")
    custom_guide = ""
    for badge in cfg.get("badges", []):
        badge_id = badge["id"]
        graphic = cfg["_badge_icons"].get(badge_id)
        art = ('<img src="' + image_uri(graphic) + '" width="26" height="26" alt="">'
               if graphic else '<span class="customBadgeSymbol" aria-hidden="true">' +
               html.escape(badge["label"][:2]) + '</span>')
        custom_guide += (
            '<dt data-project-badge="' + badge_id + '"><span class="projectBadge badgePreview customBadge">' +
            art + '</span>' + html.escape(badge["label"]) + '</dt>'
            '<dd class="customBadgeDescription"><span lang="ru">' +
            html.escape(badge["description_ru"]) + '</span><span lang="en">' +
            html.escape(badge["description_en"]) + '</span></dd>'
        )
    guide = ('<details class="badgeLegend"><summary><span aria-hidden="true">ⓘ </span>'
             '<span data-t="badgeLegend"></span></summary><dl>'
             '<dt>OG</dt><dd data-t="badgeOg"></dd>'
             '<dt>+888</dt><dd data-t="badgeFragment"></dd>'
             '<dt>0000.ton</dt><dd data-t="badgeDigits"></dd>'
             '<dt>🔥</dt><dd data-t="badgeBurn"></dd>' +
             custom_guide + '</dl></details>')
    source, count = re.subn(r'<details class="badgeLegend">.*?</details>',
                            lambda _: guide, source, count=1, flags=re.S)
    if count != 1:
        raise ProjectError("Cannot isolate foreign-project badge guide")
    cards = []
    for pool in cfg["pools"]:
        address = pool["address"]
        dexname, _, base = DEXES[pool["dex"]]
        swap = (base + "/swap?ft=" + quote(cfg["master"]) + "&tt=TON"
                if pool["dex"] == "stonfi" else base + "/swap/" + quote(cfg["master"]) + "/TON")
        actions = (
            '<a href="' + html.escape(swap, quote=True) +
            '"><span lang="ru">Обмен</span><span lang="en">Swap</span></a>' +
            '<a href="' + base + '/pools/' + address +
            '"><span lang="ru">Пул</span><span lang="en">Pool</span></a>' +
            '<a href="https://www.geckoterminal.com/ton/pools/' + address +
            '"><span lang="ru">Аналитика</span><span lang="en">Analytics</span></a>' +
            '<a href="https://gram.org/address/' + address +
            '"><span lang="ru">Контракт</span><span lang="en">Contract</span></a>')
        fee = " · " + html.escape(str(pool["fee"])) + " fee" if pool.get("fee") else ""
        cards.append('<article class="poolCard" data-quote-address="EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"><h3>' + symbol +
                     ' / TON</h3><p>' + dexname + fee +
                     '</p><div class="poolActions">' + actions + '</div></article>')
    pool_html = ('<section id="pools" class="panel resources" aria-labelledby="pools-title">'
                 '<h2 id="pools-title"><span lang="ru">🔁 Торговые пулы</span>'
                 '<span lang="en">🔁 Trading pools</span></h2>'
                 '<p class="poolIntro"><span lang="ru">Проверенные прямые пулы.</span>'
                 '<span lang="en">Verified direct pools.</span></p>'
                 '<div class="poolGrid knownPools">' + "".join(cards) + '</div>'
                 '<div class="poolGrid" id="discoveredPools" hidden></div>'
                 '<p class="poolSources" id="poolChecked"></p></section>')
    source, count = re.subn(r'<section id="pools" .*?</section>',
                            lambda _: pool_html, source, count=1, flags=re.S)
    if count != 1:
        raise ProjectError("Cannot isolate project pool directory")
    supply = ('<section id="supply" class="panel resources supplyPanel">'
              '<h2 data-t="supplyTitle"></h2>'
              '<p class="note" lang="ru">Источники заморозки и стейкинга не подключены.</p>'
              '<p class="note" lang="en">No verified lock or staking sources configured.</p>'
              '<div class="supplyGrid">'
              '<div><span data-t="supplyFrozen"></span><strong id="frozenTotal">—</strong>'
              '<small id="frozenUsd">—</small></div>'
              '<div><span data-t="supplyStaked"></span><strong id="stakingTotal">—</strong>'
              '<small id="stakingUsd">—</small></div></div></section>')
    if "staking" in cfg.get("links", {}):
        staking_url = html.escape(cfg["links"]["staking"], quote=True)
        staking_action = (
            '<div class="resourceList supplyExternal">'
            '<a href="' + staking_url + '" data-brand="project" target="_blank" '
            'rel="noopener noreferrer">'
            '<span lang="ru">Официальная страница стейкинга</span>'
            '<span lang="en">Official staking page</span></a></div>'
        )
        supply = supply.replace("</section>", staking_action + "</section>")
    source, count = re.subn(r'<section id="supply" .*?</section>',
                            lambda _: supply, source, count=1, flags=re.S)
    if count != 1:
        raise ProjectError("Cannot isolate project staking/lock integrations")
    resources = []
    for key, label in (("website", cfg["name"]), ("telegram", "Telegram"), ("x", "X"), ("staking", "Staking")):
        if key in cfg.get("links", {}):
            resources.append('<a href="' + html.escape(cfg["links"][key], quote=True) +
                             '" target="_blank" rel="noopener noreferrer">' +
                             html.escape(label) + '</a>')
    gh = "https://github.com/" + cfg["github"]["owner"] + "/" + cfg["github"]["repo"]
    resources.append('<a href="' + html.escape(gh, quote=True) + '">GitHub</a>')
    links_html = ('<section id="links" class="panel resources"><h2 data-t="links"></h2>'
                  '<div class="resourcesGrid"><article><h3 data-t="projectResources"></h3>'
                  '<div class="resourceList">' + "".join(resources) + '</div></article>'
                  '<article><h3 data-t="contractLabel"></h3>'
                  '<p class="contract" id="contractAddress"></p><div class="resourceList">'
                  '<a id="contract" data-t="exploreContract"></a><button id="copy"></button>'
                  '</div></article></div></section>')
    source, count = re.subn(r'<section id="links" .*?</section>',
                            lambda _: links_html, source, count=1, flags=re.S)
    if count != 1:
        raise ProjectError("Cannot isolate project social links")
    source, count = re.subn(
        r'<template id="badge-icon-arni">.*?</template>(?:<template .*?</template>)*',
        "", source, count=1, flags=re.S)
    if count != 1:
        raise ProjectError("Cannot remove project-specific badge images")
    return source


def app_js(source, cfg):
    source = replace(source,
                     'const MASTER="EQDbKihXMZuNfl7m7VcNrHIyYYYgCFPhccIqNN_ocNn-PBCb";',
                     'const MASTER=' + json.dumps(cfg["master"]) + ';', "master in UI")
    source, n = re.subn(r'const authorCollection="[^"]+";', 'const authorCollection="";',
                        source, count=1)
    if n != 1:
        raise ProjectError("Cannot remove NFT collection")
    source, n = re.subn(r'const projectBadgeDefs=\[.*?\];', 'const projectBadgeDefs=[];',
                        source, count=1, flags=re.S)
    if n != 1:
        raise ProjectError("Cannot remove project badges")
    # Preserve only common badges. The cloned page must never contain Ludoman
    # NFT thresholds, personal Telegram links or JVault/Arni/Joystick logic.
    shared = '''function appendProjectBadges(wrapper,wallet,verifiedDomain,ownsFragment){
  const identity=snapshot.identity?.byWallet?.[wallet];
  const badges=el("span",undefined,"projectBadges");
  if(identity?.activated){
    const date=new Date(identity.activated*1000);
    const fifth=new Date(date);
    fifth.setUTCFullYear(date.getUTCFullYear()+5);
    if(fifth.getUTCMonth()!==date.getUTCMonth())fifth.setUTCDate(0);
    if(Date.now()>fifth.getTime()){
      const badge=el("span",undefined,"projectBadge og");
      badge.append(el("span","OG"));
      badge.title=t("activated")+" "+stamp(identity.activated);
      badge.setAttribute("aria-label","OG · "+badge.title);
      badges.append(badge);
    }
  }
  const fragment=snapshot.fragmentNumbers?.byWallet?.[wallet];
  if(ownsFragment ?? (fragment?.owns && fragment.checkedAt>=Date.now()/1000-2*day)){
    const badge=el("span","+888","projectBadge fragmentNumber");
    badge.title=t("badgeFragment");
    badge.setAttribute("aria-label","+888 · "+badge.title);
    badges.append(badge);
  }
  const domains=snapshot.domains?.byWallet?.[wallet];
  const digits=numericDomains(wallet,verifiedDomain);
  appendDomainBadge(wrapper,digits.names,"digits",domains?.digitsAt,digits.linked);
  for(const definition of customBadgeDefs){
    const proof=snapshot.badges?.sources?.[definition.id];
    if(!proof || proof.asOf<Date.now()/1000-24*3600 || !proof.wallets?.[wallet])continue;
    const badge=definition.url?link(definition.url,""):el("span");
    badge.className="projectBadge customBadge";
    badge.style.setProperty("--badge-accent",definition.color||"#76bfff");
    badge.title=(lang==="ru"?definition.description_ru:definition.description_en);
    badge.setAttribute("aria-label",definition.label+" · "+badge.title);
    const image=document.querySelector(
      '#wallets .badgeLegend dt[data-project-badge="'+definition.id+'"] img');
    if(image)badge.append(image.cloneNode(true));
    else badge.append(el("span",definition.label.slice(0,2),"customBadgeSymbol"));
    badge.append(el("span",definition.label,"badgeLabel"));
    badges.append(badge);
  }
  if((burnTotals?.get(wallet)||0n)>=1000n*10n**9n){
    const badge=el("span","🔥","projectBadge burner");
    badge.title=t("burnBadge");
    badge.setAttribute("aria-label",badge.title);
    badges.append(badge);
  }
  if(badges.childElementCount)wrapper.append(badges);
}
'''
    source, n = re.subn(
        r'function appendProjectBadges\(.*?\n}\n(?=\nfunction appendDomainBadge)',
        lambda _: shared.rstrip("\n"), source, count=1, flags=re.S)
    if n != 1:
        raise ProjectError("Cannot replace legacy project-specific badge engine")
    source = source.replace('const authorCollection="";', '')
    source = source.replace('const projectBadgeDefs=[];', '')
    badge_defs = [
        {key: badge[key] for key in
         ("id", "label", "description_ru", "description_en", "url", "color")
         if key in badge}
        for badge in cfg.get("badges", [])
    ]
    badge_json = json.dumps(badge_defs, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
    source = replace(source, 'const fragmentCollection=',
                     'const customBadgeDefs=' + badge_json + ';\nconst fragmentCollection=',
                     "custom badge display configuration")
    source = replace(source,
                     'const legendBrands={"+888":"fragment","author NFT":"getgems","JVault":"jvault"};',
                     'const legendBrands={"+888":"fragment"};',
                     "foreign badge guide logos")
    source = source.replace(
        "// +888 and author NFT stay legible; their service artwork appears in the badge guide.",
        "// Common badge art and status are kept independent of project NFT collections.")
    for key in ("badgeStaking", "badgeAuthor", "badgeVnuk",
                "badgeJoystick", "badgePhoenix", "badgeBlue",
                "badgeArni", "badgeNapiwas", "badgeSub",
                "blueCollection", "supplyFrozenHint", "supplyStakedHint"):
        source = re.sub(r'("'+key+r'"\s*:\s*)"[^"]*"', r'\1""', source)
    for key in ("badgeJoystick", "badgePhoenix"):
        source, count = re.subn(
            r'(?m)^[ \t]*"' + key + r'"\s*:\s*"[^"]*",[ \t]*\n',
            '', source)
        if count != 2:
            raise ProjectError("Could not isolate bilingual project badge translation " + key)
    source = source.replace('kito:"K",', '').replace('usda:"U",', '').replace('rton:"R",', '')
    filters = [["og", "OG"], ["fragmentNumber", "+888"],
               ["digits", "0000.ton"], ["burner", "🔥 Burn"]]
    filters += [[badge["id"], badge["label"]] for badge in cfg.get("badges", [])]
    filter_js = json.dumps(filters, ensure_ascii=False, separators=(",", ":")).replace("<", r"\u003c")
    source, n = re.subn(r'const badgeFilterDefs=\[.*?\];',
                        lambda _: 'const badgeFilterDefs=' + filter_js + ';',
                        source, count=1, flags=re.S)
    if n != 1:
        raise ProjectError("Cannot remove project badge filters")
    source = replace(source, 'const brandLabels={project:"L"',
                     'const brandLabels={project:' + json.dumps(cfg["symbol"][0]),
                     "project brand fallback")
    # Project-supplied links such as the native-chain staking frontend may be
    # displayed without inventing balances, validators or yield percentages.
    source = replace(source, 'const brand=markFromLink(anchor);',
                     'const brand=anchor.dataset.brand||markFromLink(anchor);',
                     "allow explicit branding of verified service links")
    source = replace(source,
                     '".introLinks a,.resourceList a,#pools .poolActions a,#pools .poolSources a,.supplyGrid a"',
                     '".introLinks a,.resourceList a,#pools .poolActions a,#pools .poolSources a,.supplyGrid a"',
                     "preserve explicit resource icons")
    # A site's official website must receive its own token emblem, even when
    # the domain has no word "project" in it (for example tac.build).
    site = cfg.get("links", {}).get("website")
    host = urlsplit(site).hostname if site else ""
    source = replace(source, 'if(host.includes("project"))return"project";',
                     ('if(host===' + json.dumps(host) + ')return"project";') if host
                     else '/* No configured project website */', "project website emblem")
    # Differentiate unclassified smart contracts from proven service addresses.
    source = replace(source, 'identity.role;',
                     '(identity.role==="unclassified_contract" ? (lang==="ru" ? "Смарт-контракт · назначение неизвестно" : "Smart contract · purpose unverified") : identity.role);',
                     "contract classification disclosure")
    source = replace(source, 'return typeof role==="string"&&role.trim()?role.trim():null;',
                     'return typeof role==="string"&&role.trim()?role.trim():null;',
                     "service role marker")
    source = source.replace('"services": "⚙️ Сервисы"',
                            '"services": "⚙️ Сервисы и контракты"')
    source = source.replace('"services": "⚙️ Services"',
                            '"services": "⚙️ Services & contracts"')
    source = replace(source, '$("poolChecked").textContent=section?.asOf?words.checked+" · "+stamp(section.asOf):"";',
                     '$("poolChecked").textContent="";',
                     "remove dated GeckoTerminal caption")
    # Store quote contract next to each discovered pool; a spoofed ticker alone
    # must never trigger a trusted TON or USDT token flag.
    source = replace(source, 'const card=el("article",undefined,"poolCard");',
                     'const card=el("article",undefined,"poolCard");card.dataset.quoteAddress=pool.token;',
                     "pool quote master")
    source = replace(source,
                     'const tokenKind=brandLabels[quote]!==undefined?quote:(quote==="ton"?"ton":null);',
                     'const raw=rawLookupAddress(card.dataset.quoteAddress);'
                     'const native=rawLookupAddress("EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c");'
                     'const tether=rawLookupAddress("EQCxE6mUtQJKFnGfaROTKOt1lZbDiiX1kCixRv7Nw2Id_sDs");'
                     'const tokenKind=raw===native?"ton":raw===tether?"usdt":null;',
                     "only verified quote contract logos")
    # Browser storage is scoped per token even when multiple sites share an origin.
    storage_prefix = ("observatory-" + cfg["slug"] + "-" +
                      raw_address(cfg["master"]).split(":")[1][:12])
    source = replace(source, '"project-lang"',
                     json.dumps(storage_prefix + "-lang"), "per-token language storage")
    source = replace(source, '"project-currency"',
                     json.dumps(storage_prefix + "-currency"), "per-token currency storage")
    source = replace(
        source, 'item.append(check,el("span",label));list.append(item);',
        'item.append(check);'
        "const icon=document.querySelector('#wallets .badgeLegend dt[data-project-badge=\"'+key+'\"] img');"
        'if(icon)item.append(icon.cloneNode(true));'
        'item.append(el("span",label));list.append(item);',
        "show custom badge artwork inside operation filter")
    source = replace(source,
                     "const times=['trades','burns','holders'].map(k=>snapshot[k]?.asOf||0);",
                     "const required=['trades','holders'];"
                     "const times=required.map(k=>snapshot[k]?.asOf).filter(n=>Number.isFinite(n)&&n>0);"
                     "const missingSections=required.some(k=>!snapshot[k]?.asOf);",
                     "do not require unindexed burns for freshness")
    source = replace(source,
                     "const asOf=Math.min(...times), minutes=Math.max(0,Math.floor((now-asOf)/60));",
                     "const asOf=times.length?Math.min(...times):0, "
                     "minutes=asOf?Math.max(0,Math.floor((now-asOf)/60)):0;",
                     "minimum age of available verified trade and holder snapshots")
    source = replace(source, "const warning=!asOf || minutes>=150 || (snapshot.errors||[]).length>0;",
                     "const warning=!asOf || missingSections || minutes>=150 || (snapshot.errors||[]).length>0;",
                     "show partial data coverage honestly")
    source = replace(source,
                     "warning?(ru?'Часть данных устарела. Ожидаем новый снимок.':'Some data is old. Waiting for a new snapshot.'):",
                     "minutes>=150?(ru?'Данные обновляются с задержкой.':'Data refresh is delayed.'):"
                     "(missingSections||(snapshot.errors||[]).length>0)?"
                     "(ru?'Некоторые разделы пока не проиндексированы.':'Some sections have not been indexed yet.'):",
                     "distinguish absent indexing from delayed refresh")
    precision = str(cfg["decimals"])
    source = replace(source, r'!/^\d{0,9}$/.test(fraction)',
                     '!/^\\d{0,' + precision + '}$/.test(fraction)',
                     "token fractional precision")
    source = replace(source, '10n**9n', '10n**' + precision + 'n',
                     "integer token base units")
    source = replace(source, 'padEnd(9,"0")', 'padEnd(' + precision + ',"0")',
                     "fraction padding")
    source = replace(source,
                     'function volumeBars(start,end,width,left,right){\n const main=$("tradeVolume");',
                     'function volumeBars(start,end,width,left,right){\n const main=$("tradeVolume");\n'
                     ' if(!snapshot.trades){\n'
                     '   $("volumeBuys").textContent=t("buys")+" · —";\n'
                     '   $("volumeSells").textContent=t("sells")+" · —";\n'
                     '   $("volumeEmpty").hidden=false;\n'
                     '   $("volumeEmpty").textContent=t("no");\n'
                     '   main.replaceChildren();\n'
                     '   return;\n'
                     ' }\n',
                     "avoid fake zero volume before first snapshot")
    source = replace(source, 'const axisTime=seconds=>new Date(seconds*1000).toLocaleString',
                     'const axisTime=seconds=>Number.isFinite(seconds)?new Date(seconds*1000).toLocaleString',
                     "avoid invalid dates before initial snapshot")
    source = replace(source, ":{day:'numeric',month:'short',year:'2-digit'});",
                     ":{day:'numeric',month:'short',year:'2-digit'}):'—';",
                     "empty snapshot chart axis")
    return source


def python_sources(cfg, dest):
    file = dest / "assets.py"
    source = file.read_text()
    source = replace(source, 'MASTER = "EQDbKihXMZuNfl7m7VcNrHIyYYYgCFPhccIqNN_ocNn-PBCb"',
                     'MASTER = ' + repr(cfg["master"]), "token address")
    source = replace(source,
                     'MASTER_RAW = "0:db2a2857319b8d7e5ee6ed570dac72326186200853e171c22a34dfe870d9fe3c"',
                     'MASTER_RAW = ' + repr(raw_address(cfg["master"])), "raw address")
    source = replace(source, 'HOLDER_LIMIT = 100',
                     'DECIMALS = ' + str(cfg["decimals"]) + '\nHOLDER_LIMIT = 100',
                     "token precision")
    token_amount = '''def token_amount(units):
    if not re.fullmatch(r"[0-9]+", str(units)):
        raise ValueError("Invalid base-unit quantity")
    whole, fraction = divmod(int(units), 10 ** DECIMALS)
    return str(whole) if DECIMALS == 0 else (f"{whole}.{fraction:0{DECIMALS}d}").rstrip("0").rstrip(".")

def native_amount(units):
    if not re.fullmatch(r"[0-9]+", str(units)):
        raise ValueError("Invalid native TON quantity")
    whole, fraction = divmod(int(units), 10**9)
    return (f"{whole}.{fraction:09d}").rstrip("0").rstrip(".")

def resolved_domain'''
    source, n = re.subn(r'def token_amount\(units\):.*?\n\ndef resolved_domain',
                        lambda _: token_amount, source, count=1, flags=re.S)
    if n != 1:
        raise ProjectError("Missing token amount conversion")
    source = replace(source, 'int(metadata["decimals"]) != 9',
                     'int(metadata["decimals"]) != DECIMALS', "on-chain decimal validation")
    file.write_text(source)
    file = dest / "trades.py"
    source = file.read_text()
    pools = {pool["address"]: (pool["dex"], DEXES[pool["dex"]][0])
             for pool in cfg["pools"]}
    fields = 'PRIMARY = ' + repr(cfg["primary_pool"]) + '\nPOOLS = ' + repr(pools)
    source, n = re.subn(r'PRIMARY = .*?\nPOOLS = \{.*?\n\}',
                        lambda _: fields, source, count=1, flags=re.S)
    if n != 1:
        raise ProjectError("Missing legacy pool registry")
    source = replace(source, 'fetch, raw_address, token_amount',
                     'fetch, raw_address, token_amount, native_amount', "TON amount helper")
    source = replace(source,
                     'jetton, gram = token_amount(jetton), token_amount(gram)',
                     'jetton, gram = token_amount(jetton), native_amount(gram)',
                     "native TON amount is always nine decimals")
    file.write_text(source)
    file = dest / "collect.py"
    source = replace(file.read_text(),
                     '(("pools", pools.collect), ("vesting", observatory.vesting), ("staking", observatory.staking))',
                     '(("pools", pools.collect),)', "disable foreign staking integrations")
    file.write_text(source)


def build_py(cfg):
    return '''"""Bundle a configured, independent observatory into one HTML file."""
import base64
import json
from pathlib import Path
from scripts.icon_pack import embedded_script

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
        content += "\\n" + (WEB / "telegram-taste.css").read_text()
    template = template.replace(marker, content)
template = template.replace("/*ICONS*/", embedded_script())
if (WEB / "project-logo.webp").exists():
    art = "data:image/webp;base64," + base64.b64encode((WEB / "project-logo.webp").read_bytes()).decode("ascii")
else:
    art = ''' + repr(artwork(cfg)) + '''
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
payload = json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")).replace("<", r"\\u003c")
result = template.replace("__SNAPSHOT__", payload)
if any(x in result for x in ("/*APP*/", "/*STYLE*/", "/*LOADER*/", "/*MARKET_CAP*/",
                             "__PROJECT_ART__", "__PROJECT_BG__", "__BADGE_")):
    raise ValueError("Unresolved template marker")
(ROOT / "index.html").write_text(result)
'''


def workflow():
    return '''name: Update TON observatory
on:
  workflow_dispatch:
  push:
    branches: [main]
    paths:
      - '*.py'
      - 'web/**'
      - 'scripts/**'
      - 'tests/**'
      - 'project.json'
      - 'common-services.json'
      - '.github/workflows/update.yml'
permissions:
  contents: write
concurrency:
  group: observatory-data
  cancel-in-progress: false
jobs:
  refresh:
    runs-on: ubuntu-latest
    timeout-minutes: 25
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main
          fetch-depth: 20
      - name: Validate engine
        run: |
          python3 -m unittest discover -s tests -p "test_*.py"
          node --check web/app.js
          node --test tests/*.test.cjs
      - name: Collect on-chain data
        id: collect
        continue-on-error: true
        run: python3 -m scripts.refresh_observatory
      - name: Build and publish verified snapshot
        run: |
          python3 build.py
          python3 verify.py
          python3 scripts/publish_snapshot.py
      - name: Report partial collection
        if: steps.collect.outcome == 'failure'
        run: exit 1
'''


def scaffold(config_path, output):
    check_reference()
    cfg = read_config(config_path)
    if output.exists() and any(output.iterdir()):
        raise ProjectError("Target directory must be empty")
    if output.resolve() == ROOT.resolve() or ROOT.resolve().is_relative_to(output.resolve()):
        raise ProjectError("Refusing to overwrite the factory repository")
    output.mkdir(parents=True, exist_ok=True)
    for relative in CORE:
        src = source_file(relative)
        if not src.is_file():
            raise ProjectError("Missing reference: " + relative)
        dest = output / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        value = src.read_text()
        if relative in ("tests/market-cap.test.cjs", "tests/snapshot-loader.test.cjs"):
            value = value.replace("../reference/web/", "../web/")
        if relative == "web/snapshot-loader.js":
            value = replace(value, "Freebielife/Ludoman",
                            cfg["github"]["owner"] + "/" + cfg["github"]["repo"],
                            "GitHub snapshot URL")
        if relative not in ("common-services.json", "service_registry.py", "tests/test_service_registry.py"):
            value = generic(value, cfg)
        if relative in ("assets.py", "trades.py", "collect.py", "verify.py",
                        "web/app.js", "web/market-cap.js",
                        "tests/market-cap.test.cjs"):
            value = schema(value)
        if relative == "tests/market-cap.test.cjs":
            value = replace(value, "project:String(project)",
                            "tokenAmount:String(project)", "generic market-cap fixture")
            value = value.replace("=>({time,", "=>({pool:" + json.dumps(cfg["primary_pool"]) + ",time,")
            value = value.replace("...row(190,10),dex:'DeDust'",
                                  "...row(190,10),dex:'DeDust',pool:'other-pool'")
            value = value.replace("filters out DeDust prices", "filters other pool prices")
        if relative == "assets.py":
            value = replace(
                value,
                r'DOMAIN = re.compile(r"(?!(?:[a-z0-9-]+\.)*socool\.ton$)(?:[a-z0-9-]+\.)+ton")',
                r'DOMAIN = re.compile(r"(?:[a-z0-9-]+\.)+ton")',
                "remove project-specific socool.ton domain exclusion")
        if relative == "web/app.js":
            value = app_js(value, cfg)
        if relative == "web/telegram-taste.css":
            value += ('\nhtml[lang="ru"] #supply [lang="en"], '
                      'html[lang="en"] #supply [lang="ru"]{display:none!important}\n')
            value += '''
/* Token symbol is private to the newly generated project, not the common flags. */
.brandGlyph.brand-project{background:var(--project-art) center/contain no-repeat!important;
 border-color:transparent!important;box-shadow:none!important;
 color:transparent!important;font-size:0!important;padding:0!important}
.supplyExternal{display:flex;flex-wrap:wrap;margin-top:14px;gap:9px}
.supplyExternal a{display:inline-flex;align-items:center;gap:8px;
 text-decoration:none;color:#eff8ff;border:1px solid #567296;
 background:#132447;border-radius:10px;padding:9px 12px;min-height:42px}
.supplyExternal a:hover{border-color:#81bdff}
html[lang="en"] .supplyExternal [lang="ru"],
html[lang="ru"] .supplyExternal [lang="en"]{display:none!important}
'''
            value += '''
/* Project-specific badges (both static WebP and animated WebP/GIF). */
#wallets .badgeLegend dt[data-project-badge] {display:flex;gap:8px;align-items:center}
#wallets .badgeLegend dt[data-project-badge] .customBadge {flex:0 0 31px}
#wallets .badgeLegend dt[data-project-badge] img {width:26px;height:26px;object-fit:contain}
html[lang="en"] .customBadgeDescription [lang="ru"] {display:none!important}
html[lang="ru"] .customBadgeDescription [lang="en"] {display:none!important}
.projectBadge.customBadge {display:inline-flex;gap:5px;align-items:center;
  color:#f0f8ff;background:linear-gradient(120deg,#172b40,#23435a);
  border:1px solid var(--badge-accent,#76bfff);border-radius:9px;
  padding:3px 7px;min-height:25px}
#badgeFilterList .badgeFilterItem img {width:22px;height:22px;object-fit:contain;flex:0 0 22px}
.projectBadge.customBadge img {width:23px;height:23px;object-fit:contain;
  animation:customBadgeFloat 2.8s ease-in-out infinite alternate}
.projectBadge.customBadge .customBadgeSymbol {font-size:12px;font-weight:850;
  color:var(--badge-accent,#76bfff);min-width:20px;text-align:center}
@keyframes customBadgeFloat {from{transform:translateY(1px) scale(.95)}
 to{transform:translateY(-1px) scale(1.05)}}
@media(prefers-reduced-motion:reduce) {
 .projectBadge.customBadge img {animation:none!important}
}
'''
        if relative == "pools.py":
            value = value.replace('"TON (TON)"', '"TON"')
        elif relative == "web/page.html":
            value = page_html(value, cfg)
        elif relative == "web/market-cap.js":
            value = replace(value, '(!r.dex||r.dex==="STON.fi")',
                            'r.pool===' + json.dumps(cfg["primary_pool"]),
                            "exact source pool for market chart")
        elif relative == "scripts/icon_pack.py":
            value = replace(
                value, '    data=json.loads((root/"approved-brand-atlas.json").read_text())',
                '    if not (root/"approved-brand-atlas.json").exists():\n'
                '        return {"image":"","cols":0,"rows":0,"positions":{}}\n'
                '    data=json.loads((root/"approved-brand-atlas.json").read_text())',
                "isolated brand atlas")
        dest.write_text(value)
    pack = output / "assets/icon-pack"
    for relative in COMMON_SVGS:
        dest = pack / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "assets/icon-pack" / relative, dest)
    manifest = json.loads((ROOT / "assets/icon-pack/manifest.json").read_text())
    manifest["assets"] = [x for x in manifest["assets"] if x["file"] in COMMON_SVGS]
    manifest["pending"] = []
    (pack / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    # Physically redact other tokens from the shared TONecoFlags sprite.
    shared = build_common_atlas(ROOT / "assets/icon-pack/approved-brand-atlas.json")
    (pack / "approved-brand-atlas.json").write_text(
        json.dumps(shared, ensure_ascii=False, separators=(",", ":")))
    (output / "badges.py").write_text(common_badges(source_file("badges.py").read_text(), cfg))
    (output / "observatory.py").write_text(common_observatory(
        source_file("observatory.py").read_text(), cfg))
    python_sources(cfg, output)
    (output / "build.py").write_text(build_py(cfg))
    (output / ".github/workflows").mkdir(parents=True, exist_ok=True)
    (output / ".github/workflows/update.yml").write_text(workflow())
    (output / "data").mkdir()
    (output / "data/snapshot.json").write_text(json.dumps({
        "schema": 1, "token": cfg["master"], "updated": 1,
        "errors": ["holders", "trades", "burns", "domains", "rates"]}))
    exported = {k: v for k, v in cfg.items() if not k.startswith("_")}
    if "_logo" in cfg:
        exported["logo_file"] = "web/project-logo.webp"
    if "_background" in cfg:
        exported["background_file"] = "web/project-background.webp"
    for badge in exported.get("badges", []):
        if badge["id"] in cfg["_badge_icons"]:
            badge["icon_file"] = ("web/badges/" + badge["id"] +
                                  cfg["_badge_icons"][badge["id"]].suffix.lower())
    (output / "project.json").write_text(
        json.dumps(exported, ensure_ascii=False, indent=2))
    if cfg.get("_logo"):
        shutil.copy2(cfg["_logo"], output / "web/project-logo.webp")
    if cfg.get("_background"):
        shutil.copy2(cfg["_background"], output / "web/project-background.webp")
    if cfg["_badge_icons"]:
        (output / "web/badges").mkdir(exist_ok=True)
        for key, original in cfg["_badge_icons"].items():
            shutil.copy2(original, output / ("web/badges/" + key + original.suffix.lower()))
    (output / ".gitignore").write_text("build/\n__pycache__/\n*.pyc\n")
    (output / "README.md").write_text(
        "# " + cfg["name"] + " Observatory\n\n"
        + description_section(cfg.get("project_description")) +
        "Generated from https://github.com/Freebielife/TON-Observatory-Template.\n\n"
        "Run python3 -m scripts.refresh_observatory; python3 build.py; python3 verify.py.\n"
        "Publish index.html in TON Sites only after independent on-chain verification.\n"
        "The initial snapshot is EMPTY: no market data is claimed.\n"
        "Only native TON swap pairs supported. Locks, staking and custom project NFT "
        "badges are configured through project.json and verified against TonAPI.\n"
        "Configure your GitHub workflow scheduler before launch.\n")
    banned = ("EQDbKihXMZuNfl7m7VcNrHIyYYYgCFPhccIqNN_ocNn-PBCb",
              "the1000ludoman", "1000ludoman.xyz", "CryptoCheck",
              "mRvnukICHlife", "joystickpro", "PHXPW", "TonArnold",
              "NAPIWASofficial", "__BADGE_")
    for relative in ("web/page.html", "web/app.js", "web/market-cap.js",
                     "web/style.css", "web/telegram-taste.css",
                     "assets.py", "trades.py", "observatory.py", "badges.py"):
        text = (output / relative).read_text()
        if any(x.lower() in text.lower() for x in banned):
            raise ProjectError("Foreign-project reference survived: " + relative)
    if set(p.name for p in (output / "web").glob("*.webp")) - {"project-logo.webp", "project-background.webp"}:
        raise ProjectError("Foreign token artwork survived the build")
    install_foundation(output, cfg)
    install_branding(output, cfg, ROOT / "assets/icon-pack/approved-brand-atlas.json")
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generate a project-isolated TON Observatory")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    options = parser.parse_args(argv)
    try:
        target = scaffold(options.config, options.output)
    except (ProjectError, OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print("Created isolated observatory: " + str(target))
    print("Validate on-chain pools, then collect verified data before publishing.")


if __name__ == "__main__":
    main()
