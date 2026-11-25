"""Audited, self-contained SVG icon pack for TON observatories."""
from __future__ import annotations
import base64
import json
from pathlib import Path
import sys
from html import escape
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PACK_ROOT=ROOT/"assets"/"icon-pack"
ALLOWED={"svg","title","path","g","rect","circle","ellipse","line","polyline",
         "polygon","defs","linearGradient","stop"}

def validate_svg(raw: str)->None:
    tree=ET.fromstring(raw)
    assert tree.tag.split("}")[-1]=="svg", "Not SVG"
    for el in tree.iter():
        if el.tag.split("}")[-1] not in ALLOWED:
            raise ValueError("Unexpected SVG element")
        for key,value in el.attrib.items():
            name=key.split("}")[-1].lower()
            if name.startswith("on") or name in ("href","src"):
                raise ValueError("Script/external SVG reference forbidden")
            if "url(" in value.lower() or "javascript:" in value.lower():
                raise ValueError("Unsafe SVG value")

def load_pack(root: Path=PACK_ROOT)->dict[str,str]:
    manifest=json.loads((root/"manifest.json").read_text())
    out={}
    for entry in manifest["assets"]:
        path=Path(entry["file"])
        if path.is_absolute() or ".." in path.parts or path.suffix!=".svg" or path.parts[0] not in ("ui","brands"):
            raise ValueError("Invalid icon path")
        raw=(root/path).read_text()
        validate_svg(raw)
        out[entry["id"]]="data:image/svg+xml;base64,"+base64.b64encode(raw.encode()).decode()
    return out

def load_brand_atlas(root: Path=PACK_ROOT)->dict:
    """Load the owner-approved static emoji atlas, validating it before embedding."""
    data=json.loads((root/"approved-brand-atlas.json").read_text())
    rows,cols=data["rows"],data["columns"]
    if not isinstance(rows,int) or not isinstance(cols,int) or not (1<rows<=8 and 1<cols<=8):
        raise ValueError("Invalid brand atlas grid")
    image_data=base64.b64decode(data["image_base64"],validate=True)
    if not image_data.startswith(b"RIFF") or image_data[8:12]!=b"WEBP" or len(image_data)>128000:
        raise ValueError("Invalid or oversized brand WebP atlas")
    positions=data["positions"]
    if not isinstance(positions,dict) or not positions or any(
        not isinstance(name,str) or not isinstance(cell,list) or len(cell)!=2 or
        not all(isinstance(v,int) for v in cell) or
        not (0<=cell[0]<cols and 0<=cell[1]<rows)
        for name,cell in positions.items()
    ):
        raise ValueError("Invalid brand atlas positions")
    return {"image":"data:image/webp;base64,"+data["image_base64"],
            "cols":cols,"rows":rows,"positions":positions}

def embedded_script(root: Path=PACK_ROOT)->str:
    icons="window.OBSERVATORY_ICON_PACK=Object.freeze("+json.dumps(load_pack(root),separators=(",",":"))+");"
    brands="window.OBSERVATORY_BRAND_ATLAS=Object.freeze("+json.dumps(load_brand_atlas(root),separators=(",",":"))+");"
    return icons+brands

def gallery(root: Path=PACK_ROOT, output: Path=ROOT/"build"/"icon-gallery.html")->Path:
    manifest=json.loads((root/"manifest.json").read_text())
    icons=load_pack(root)
    tiles="".join('<article><div class="icon"><img src="'+icons[i["id"]]+'" alt=""></div>'+
                  '<strong>'+escape(i["id"])+'</strong><small>'+escape(i["provider"])+'</small></article>'
                  for i in manifest["assets"])
    pending="".join('<li><b>'+escape(i["name"])+'</b> — '+escape(i["status"])+'</li>'
                    for i in manifest["pending"])
    html=('<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
          '<title>TON Observatory — каталог иконок</title><style>'
          ':root{color-scheme:dark}*{box-sizing:border-box}body{background:#0b1322;color:#eef6ff;'
          'font:15px system-ui;margin:0;padding:24px}.wrap{max-width:1000px;margin:auto}'
          '.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:12px}'
          'article{background:#172b41;border:1px solid #36536d;border-radius:14px;padding:16px;'
          'display:grid;gap:8px;justify-items:center;min-width:0}.icon{width:60px;height:60px;'
          'border-radius:16px;background:#315475;display:grid;place-items:center}.icon img{width:35px;'
          'height:35px;filter:brightness(0) invert(1)}small{font-size:11px;color:#bdd0e2}'
          'li{margin:7px 0}h1{font-size:clamp(22px,4vw,40px)}</style><div class="wrap">'
          '<h1>TON Observatory · Иконки</h1><p>Подготовленные SVG. Без внешних ресурсов.</p>'
          '<div class="grid">'+tiles+'</div><h2>Требуются оригиналы или проверка</h2><ul>'
          +pending+'</ul></div></html>')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(html)
    return output

if __name__=="__main__" and "--gallery" in sys.argv:
    print(gallery())
