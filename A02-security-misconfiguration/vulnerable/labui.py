"""
Общий веб-интерфейс лаб: страница /ui.

Это учебная обвязка, а НЕ часть уязвимости: страница строится по списку
маршрутов Flask, поэтому для vulnerable и fixed она одинаковая, а
эндпоинты в ней всегда совпадают с реальными. В браузере адрес "/"
перенаправляет на /ui; curl/Postman получают прежний ответ "/".
"""
import json
import re

from flask import Response, redirect, request

_HELPERS = re.compile(r"^/(reset-lab|_lab/|mirror/|cdn/compromise|system/)")


def _endpoints(app, presets):
    out = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static" or rule.rule in ("/ui", "/favicon.ico"):
            continue
        path = re.sub(r"<int:[^>]+>", "1", rule.rule)
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            out.append({
                "method": method,
                "path": path,
                "helper": bool(_HELPERS.match(rule.rule)),
                "presets": presets.get(f"{method} {rule.rule}", []),
            })
    out.sort(key=lambda e: (e["helper"], e["path"] != "/", e["path"], e["method"]))
    return out


def register_ui(app, title, notes="", presets=None):
    """presets: {"POST /login": [("alice", {"username": ...}), ...]}
    значение dict -> тело запроса; str -> добавляется к пути (или заменяет
    его, если начинается с "/")."""
    presets = presets or {}

    @app.before_request
    def _ui_redirect():
        if (request.path == "/" and request.method == "GET"
                and request.accept_mimetypes.best == "text/html"):
            return redirect("/ui")

    @app.get("/ui")
    def _ui():
        data = json.dumps({"title": title, "notes": notes,
                           "endpoints": _endpoints(app, presets)},
                          ensure_ascii=False).replace("</", "<\\/")
        return Response(_PAGE.replace("__DATA__", data),
                        mimetype="text/html")


_PAGE = r"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Лаба</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--fg:#1c2330;--mut:#5f6b7a;--line:#d9dee5;
--acc:#2457d6;--ok:#12805c;--bad:#c2362b;--code:#eef1f5}
@media (prefers-color-scheme:dark){:root{--bg:#12161c;--card:#1b212a;--fg:#e6eaf0;
--mut:#93a0b0;--line:#2d3642;--acc:#6b9bff;--ok:#3ecf9a;--bad:#ff7b6f;--code:#11151b}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{padding:18px 24px;border-bottom:1px solid var(--line);background:var(--card)}
h1{margin:0;font-size:20px}header p{margin:4px 0 0;color:var(--mut)}
main{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px;
padding:20px 24px;align-items:start}
@media (max-width:900px){main{grid-template-columns:1fr}}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.06em;color:var(--mut);margin:0 0 10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;
padding:12px 14px;margin-bottom:10px}
.row{display:flex;gap:8px;align-items:center}
.m{font:600 12px ui-monospace,Consolas,monospace;padding:3px 7px;border-radius:5px;
background:var(--code);min-width:52px;text-align:center}
.m.GET{color:var(--ok)}.m.POST{color:var(--acc)}
input,textarea{width:100%;background:var(--code);color:var(--fg);border:1px solid var(--line);
border-radius:6px;padding:7px 9px;font:13px ui-monospace,Consolas,monospace}
textarea{margin-top:8px;min-height:64px;resize:vertical}
button{background:var(--acc);color:#fff;border:0;border-radius:6px;padding:7px 14px;
font:600 13px inherit;cursor:pointer}
button.s{background:var(--code);color:var(--fg);border:1px solid var(--line);font-weight:500;
padding:4px 9px;font-size:12px}
.pre{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px;align-items:center}
.tag{font-size:11px;color:var(--mut);border:1px solid var(--line);border-radius:4px;padding:1px 6px}
#out{position:sticky;top:12px}
pre{margin:0;white-space:pre-wrap;word-break:break-word;background:var(--code);
border-radius:6px;padding:10px;font:13px/1.45 ui-monospace,Consolas,monospace;
max-height:55vh;overflow:auto}
#st{font-weight:600;margin-bottom:8px}.ok{color:var(--ok)}.bad{color:var(--bad)}
.hint{color:var(--mut);font-size:12px;margin-top:6px}
a{color:var(--acc)}
</style></head><body>
<header><h1 id="t"></h1><p id="n"></p></header>
<main>
<section id="eps"><h2>Эндпоинты</h2></section>
<section id="out">
<h2>Ответ сервера</h2>
<div class="card"><div id="st" class="hint">Отправьте запрос слева.</div>
<pre id="body"></pre><div class="hint" id="hd"></div></div>
<h2>Cookie этого сайта</h2>
<div class="card"><pre id="ck"></pre>
<div class="row" style="margin-top:8px"><input id="cv" placeholder="имя=значение">
<button class="s" id="cs">Задать</button><button class="s" id="cc">Очистить</button></div>
<div class="hint">Видны только cookie без флага HttpOnly. Заданная здесь cookie
уходит со следующими запросами.</div></div>
</section></main>
<script id="d" type="application/json">__DATA__</script>
<script>
const D2=JSON.parse(document.getElementById('d').textContent);
document.title=D2.title;
document.getElementById('t').textContent=D2.title;
document.getElementById('n').textContent=D2.notes;
const $=(i)=>document.getElementById(i);
function cookies(){$('ck').textContent=document.cookie?document.cookie.split('; ').join('\n'):'(пусто)';}
$('cs').onclick=()=>{if($('cv').value.includes('=')){document.cookie=$('cv').value+'; path=/';$('cv').value='';cookies();}};
$('cc').onclick=()=>{document.cookie.split('; ').forEach(c=>{const n=c.split('=')[0];
if(n)document.cookie=n+'=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';});cookies();};
function el(tag,cls,txt){const e=document.createElement(tag);if(cls)e.className=cls;
if(txt!==undefined)e.textContent=txt;return e;}
let helpers=false;
function card(e){
  const c=el('div','card'),r=el('div','row'),m=el('span','m '+e.method,e.method);
  const p=el('input');p.value=e.path;p.spellcheck=false;
  const go=el('button',null,'Отправить');
  r.append(m,p,go);c.append(r);
  let ta=null;
  if(e.method!=='GET'){ta=el('textarea');ta.placeholder='{"ключ": "значение"}';ta.spellcheck=false;c.append(ta);}
  if(e.presets.length){
    const pr=el('div','pre');pr.append(el('span','tag','примеры'));
    e.presets.forEach(([label,val])=>{const b=el('button','s',label);
      b.onclick=()=>{if(typeof val==='string'){p.value=val.startsWith('/')?val:e.path.replace(/\?.*/,'')+val;}
        else if(ta)ta.value=JSON.stringify(val,null,2);};
      pr.append(b);});
    c.append(pr);
  }
  if(e.method==='GET'){const a=el('a',null,'открыть в новой вкладке ↗');a.target='_blank';
    a.onclick=()=>{a.href=p.value;};a.href=p.value;
    const w=el('div','hint');w.append(a);c.append(w);}
  go.onclick=async()=>{
    const o={method:e.method,credentials:'same-origin',headers:{}};
    if(ta&&ta.value.trim()){o.headers['Content-Type']='application/json';o.body=ta.value;}
    const t0=performance.now();
    try{
      const res=await fetch(p.value,o),txt=await res.text();
      let shown=txt;try{shown=JSON.stringify(JSON.parse(txt),null,2);}catch(_){}
      $('st').textContent=res.status+' '+res.statusText+'  ·  '+Math.round(performance.now()-t0)+' мс';
      $('st').className=res.ok?'ok':'bad';
      $('body').textContent=shown||'(пустое тело)';
      $('hd').textContent='Content-Type: '+(res.headers.get('content-type')||'—')
        +(res.redirected?'  ·  был редирект на '+res.url:'');
    }catch(err){$('st').textContent='Ошибка сети: '+err;$('st').className='bad';$('body').textContent='';}
    cookies();
  };
  return c;
}
function render(){
  const box=$('eps');box.querySelectorAll('.card,.hint,.tag2').forEach(n=>n.remove());
  D2.endpoints.filter(e=>!e.helper).forEach(e=>box.append(card(e)));
  const hs=D2.endpoints.filter(e=>e.helper);
  if(hs.length){
    const h=el('h2',null,'Лабораторные помощники');h.className='tag2';h.style.marginTop='18px';
    h.id='hh';box.append(h);
    box.append(el('div','hint','Имитируют окружение (сброс, «взломанный» CDN, зеркало и т.п.), не часть приложения.'));
    hs.forEach(e=>box.append(card(e)));
  }
}
render();cookies();
</script></body></html>"""
