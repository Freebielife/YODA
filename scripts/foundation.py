"""Apply shared foundation features to isolated factory output, never to a live token."""
import json
from scripts.project_runtime import VERSION


def install(output, cfg):
    # Keep display limits independent of the collector's 100-account sample.
    app = output / "web/app.js"
    text = app.read_text()
    required = ('function ranks(){', '$("rank").replaceChildren(...data.map((r,i)=>{',
                ' if(!data.length)$("rank").append', " $('syncDetail').textContent=detail;",
                ' if(!combined.length)$("feed").append(el("p",t(large?')
    if any(marker not in text for marker in required):
        raise ValueError("Factory UI changed; foundation integration must be reviewed")
    text = text.replace('function ranks(){', 'let holdersExpanded=false;\nfunction ranks(){', 1)
    text = text.replace('i=>{ranking=views[i];ranks()}', 'i=>{ranking=views[i];holdersExpanded=false;ranks()}', 1)
    text = text.replace('$("rank").replaceChildren(...data.map((r,i)=>{',
        'const visibleRanks=isHolder&&!holdersExpanded?data.slice(0,10):data;\n'
        ' $("rank").replaceChildren(...visibleRanks.map((r,i)=>{', 1)
    text = text.replace(' if(!data.length)$("rank").append', ''' const more=$("holdersMore");
 more.hidden=!isHolder||data.length<=10;
 more.setAttribute("aria-expanded",String(holdersExpanded));
 more.textContent=holdersExpanded?(lang==="ru"?"⌃ Свернуть до 10":"⌃ Show top 10"):(lang==="ru"?"⌄ Показать топ 20":"⌄ Show top 20");
 more.onclick=()=>{holdersExpanded=!holdersExpanded;ranks()};
 if(!data.length)$("rank").append''', 1)
    # An absent/failed source is not a verified empty activity history.
    text = text.replace(' if(!combined.length)$("feed").append(el("p",t(large?',
        ' const needed=feedKind==="burn"?["burns","zeroBurns"]:feedKind==="all"?["trades","burns","zeroBurns"]:["trades"];\n'
        ' const feedUnavailable=needed.some(key=>!snapshot[key]||(snapshot.errors||[]).includes(key));\n'
        ' if(!combined.length)$("feed").append(el("p",feedUnavailable?t("no"):t(large?')
    # Missing trade history must not assert that no sellers exist.
    text = text.replace('source?t("none"):t("no")',
                        '(source&&!(snapshot.errors||[]).includes(isHolder||isService?"holders":"trades"))?t("none"):t("no")')
    # Include source-specific times/errors in existing status UI, after every refresh.
    text = text.replace(' $(\'syncDetail\').textContent=detail;', ''' const labels=ru?{holders:"Холдеры",trades:"Операции / график",burns:"Сжигания",pools:"Пулы",domains:"Домены"}:{holders:"Holders",trades:"Trades / chart",burns:"Burns",pools:"Pools",domains:"Domains"};
 $('sectionStatusTitle').textContent=ru?'Актуальность разделов':'Section freshness';
 $('sectionStatusRows').replaceChildren(...Object.entries(labels).map(([key,label])=>{
   const part=snapshot[key],unavailable=(snapshot.errors||[]).includes(key);
   return el('p',label+': '+(part?.asOf?stamp(part.asOf):(ru?'нет данных':'unavailable'))+(unavailable?(ru?' (ошибка обновления)':' (refresh failed)'):''));
 }));
 $('syncDetail').textContent=detail;''', 1)
    # Expose provenance where a person is choosing whether to trust an attribution.
    text = text.replace('const address=addr(raw,(holder&&identity?.role)||domain||name);',
        'const address=addr(raw,(holder&&identity?.role)||domain||name);\n'
        '  if(identity?.roleSource)address.title=(identity.serviceCategory||"service")+" · "+identity.roleSource;')
    text = text.replace("minutes>=150", "minutes>=60")
    app.write_text(text)
    page = output / "web/page.html"
    page.write_text(page.read_text().replace('<div id="rank"></div>',
        '<div id="rank"></div><button id="holdersMore" type="button" class="more" aria-controls="rank" aria-expanded="false" hidden></button>'))
    page.write_text(page.read_text().replace('<small id="syncDetail"></small>',
        '<small id="syncDetail"></small><details id="sectionStatus"><summary id="sectionStatusTitle"></summary><div id="sectionStatusRows"></div></details>'))
    style = output / "web/telegram-taste.css"
    style.write_text(style.read_text()+'''\n#holdersMore{display:block;margin:16px auto 0;min-height:44px;max-width:100%;padding:10px 18px;border:1px solid #567296;border-radius:10px;background:#132447;color:#eff8ff;cursor:pointer;font:inherit}
#holdersMore[hidden]{display:none!important}
#syncDetail,#sectionStatus{overflow-wrap:anywhere}
#sectionStatus{margin-top:8px;font-size:14px}#sectionStatus summary{cursor:pointer;min-height:32px}#sectionStatus p{margin:6px 0}
''')
    # Builders check identity and size before replacing the previous working file.
    build = output / "build.py"
    value = build.read_text().replace('from scripts.icon_pack import embedded_script',
        'from scripts.icon_pack import embedded_script\nfrom scripts.project_runtime import publish_html')
    value = value.replace('(ROOT / "index.html").write_text(result)',
                          'publish_html(ROOT, result, snapshot)')
    build.write_text(value)
    runner = output / "scripts/refresh_observatory.py"
    value = runner.read_text().replace('import domains', 'import domains\nfrom scripts.project_runtime import read_project, check_identity, decorate_snapshot')
    value = value.replace('    SNAPSHOT.parent.mkdir', '    project = read_project(ROOT)\n    check_identity(snapshot, project)\n    decorate_snapshot(snapshot, project)\n    SNAPSHOT.parent.mkdir', 1)
    value = value.replace('    errors = set(snap.get("errors", ()))', '    check_identity(snap, read_project(ROOT))\n    errors = set(snap.get("errors", ()))', 1)
    value = value.replace('            errors.discard(key)', '            if key == "badges" and result.get("failed"):\n                errors.add(key)\n            else:\n                errors.discard(key)', 1)
    value = value.replace('        prior = snap.get(key, {})', '        prior = snap.get(key, {})\n        snap.setdefault("refreshStatus", {})[key] = {"attemptedAt": now, "ok": None}', 1)
    value = value.replace('            save(snap)\n            print(key, "SAVED"', '            snap["refreshStatus"][key].update(ok=key not in errors, lastSuccess=result["asOf"])\n            save(snap)\n            print(key, "SAVED"', 1)
    value = value.replace('            errors.add(key)\n            snap["errors"]', '            errors.add(key)\n            snap["refreshStatus"][key].update(ok=False, error=type(exc).__name__, lastSuccess=prior.get("asOf"))\n            snap["errors"]', 1)
    runner.write_text(value)
    exported = output / "project.json"
    project = json.loads(exported.read_text())
    project.update(template_repository="Freebielife/TON-Observatory-Template", engine_version=VERSION, max_html_bytes=cfg.get("max_html_bytes", 2_500_000),
        ui={"holders_initial": 10, "holders_expanded": 20},
        methodology={"valuation": "last observed swap in primary_pool times CURRENT total supply; not circulating market cap",
                     "primary_pool": cfg["primary_pool"], "sellers": "sum of successful supported native TON swap sales; service roles excluded",
                     "holders": "balances excluding known services and identified contracts; unclassified accounts may remain until verified",
                     "burns": "accepted burn notifications and zero-address transfers shown as distinct evidence",
                     "usd": "historical TON/USD rate from CoinGecko", "history": "incremental confirmed swaps; missing intervals remain partial"})
    exported.write_text(json.dumps(project, ensure_ascii=False, indent=2))
    (output / "ENGINE_VERSION").write_text(VERSION+"\n")
    readme = output / "README.md"
    readme.write_text(readme.read_text()+'''\nFoundation version: '''+VERSION+'''. Holders show 10, expandable to top 20.
`project.json` is the per-project specification. Contract/pool/precision changes require regenerating from the factory; do not reuse another token's snapshot.
Run `python3 build.py` for an atomic bundle and `build/report.json` size report.
No external fonts, scripts or images are needed to render the saved page. Fresh data checks and manual wallet lookups require network access.
Cloudflare dispatch registration and GitHub repository access remain separate deployment steps. No credentials go into HTML.
''')
