"""
Общий веб-интерфейс лаб: страница /ui.

Это учебная обвязка, а НЕ часть уязвимости: страница строится по списку
маршрутов Flask, поэтому для vulnerable и fixed она одинаковая, а
эндпоинты в ней всегда совпадают с реальными. В браузере адрес "/"
перенаправляет на /ui; curl/Postman получают прежний ответ "/".

Языки интерфейса: русский (по умолчанию) и узбекский. Переключатель RU/UZ
появляется только если лаба передала параметр uz в register_ui; выбор
запоминается в браузере, его можно задать и в адресе: /ui?lang=uz.
Файл одинаковый во всех лабах (копируйте его целиком).
"""
import json
import re

from flask import Response, redirect, request

_HELPERS = re.compile(r"^/(reset-lab|_lab/|mirror/|cdn/compromise|system/)")


def _endpoints(app, presets_by_lang):
    out = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint == "static" or rule.rule in ("/ui", "/favicon.ico"):
            continue
        path = re.sub(r"<int:[^>]+>", "1", rule.rule)
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            key = f"{method} {rule.rule}"
            out.append({
                "method": method,
                "path": path,
                "helper": bool(_HELPERS.match(rule.rule)),
                "presets": {lang: p.get(key, [])
                            for lang, p in presets_by_lang.items()},
            })
    out.sort(key=lambda e: (e["helper"], e["path"] != "/", e["path"], e["method"]))
    return out


def register_ui(app, title, notes="", presets=None, uz=None):
    """presets: {"POST /login": [("alice", {"username": ...}), ...]}
    значение dict -> тело запроса; str -> добавляется к пути (или заменяет
    его, если начинается с "/").

    uz (необязательно): узбекская версия данных лабы, например
    {"notes": "...", "presets": {"POST /guestbook": [("yozuv", {...})]}}.
    Ключи presets из uz заменяют русские списки целиком, остальные берутся
    из presets без изменений."""
    presets = presets or {}
    langs = {"ru": {"notes": notes, "presets": presets}}
    if uz:
        langs["uz"] = {"notes": uz.get("notes", notes),
                       "presets": {**presets, **uz.get("presets", {})}}

    @app.before_request
    def _ui_redirect():
        # браузер всегда называет text/html в Accept; curl/Postman шлют */*
        if (request.path == "/" and request.method == "GET"
                and "text/html" in request.headers.get("Accept", "")):
            return redirect("/ui")

    @app.get("/ui")
    def _ui():
        data = json.dumps({
            "title": title,
            "langs": list(langs),
            "notes": {k: v["notes"] for k, v in langs.items()},
            "endpoints": _endpoints(app, {k: v["presets"] for k, v in langs.items()}),
        }, ensure_ascii=False).replace("</", "<\\/")
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
header{padding:18px 24px;border-bottom:1px solid var(--line);background:var(--card);
display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
h1{margin:0;font-size:20px}header p{margin:4px 0 0;color:var(--mut)}
.lg{display:flex;gap:6px}.lg[hidden]{display:none}
button.on{background:var(--acc)!important;color:#fff!important;border-color:var(--acc)!important}
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
<header><div><h1 id="t"></h1><p id="n"></p></div>
<div class="lg" id="lg" hidden><button class="s" data-l="ru">RU</button><button class="s" data-l="uz">UZ</button></div></header>
<main>
<section id="eps"><h2 id="h-eps"></h2></section>
<section id="out">
<h2 id="h-out"></h2>
<div class="card"><div id="st" class="hint" data-init="1"></div>
<pre id="body"></pre><div class="hint" id="hd"></div></div>
<h2 id="h-ck"></h2>
<div class="card"><pre id="ck"></pre>
<div class="row" style="margin-top:8px"><input id="cv">
<button class="s" id="cs"></button><button class="s" id="cc"></button></div>
<div class="hint" id="ck-hint"></div></div>
</section></main>
<script id="d" type="application/json">__DATA__</script>
<script>
const D2=JSON.parse(document.getElementById('d').textContent);
const $=(i)=>document.getElementById(i);
const S={
ru:{eps:'Эндпоинты',out:'Ответ сервера',send_left:'Отправьте запрос слева.',
ck:'Cookie этого сайта',cv:'имя=значение',set:'Задать',clear:'Очистить',
ck_hint:'Видны только cookie без флага HttpOnly. Заданная здесь cookie уходит со следующими запросами.',
empty:'(пусто)',send:'Отправить',body_ph:'{"ключ": "значение"}',presets:'примеры',
newtab:'открыть в новой вкладке ↗',ms:' мс',empty_body:'(пустое тело)',
redir:'  ·  был редирект на ',neterr:'Ошибка сети: ',helpers:'Лабораторные помощники',
helpers_hint:'Имитируют окружение (сброс, «взломанный» CDN, зеркало и т.п.), не часть приложения.'},
uz:{eps:'Endpointlar',out:'Server javobi',send_left:'Chapdan soʻrov yuboring.',
ck:'Ushbu saytning cookie lari',cv:'nom=qiymat',set:'Oʻrnatish',clear:'Tozalash',
ck_hint:'Faqat HttpOnly bayrogʻisiz cookie lar koʻrinadi. Bu yerda oʻrnatilgan cookie keyingi soʻrovlar bilan yuboriladi.',
empty:'(boʻsh)',send:'Yuborish',body_ph:'{"kalit": "qiymat"}',presets:'namunalar',
newtab:'yangi varaqda ochish ↗',ms:' ms',empty_body:'(boʻsh javob tanasi)',
redir:'  ·  yoʻnaltirildi: ',neterr:'Tarmoq xatosi: ',helpers:'Laboratoriya yordamchilari',
helpers_hint:'Muhitni imitatsiya qiladi (tiklash, «buzilgan» CDN, oyna va h.k.), ilovaning qismi emas.'}
};
function pickLang(){
  let l=null;
  try{l=new URLSearchParams(location.search).get('lang')||localStorage.getItem('lab_lang');}catch(_){}
  if(!l){try{if(/^uz/i.test(navigator.language||''))l='uz';}catch(_){}}
  return D2.langs.includes(l)?l:D2.langs[0];
}
let lang=pickLang();
const T=(k)=>S[lang][k];
document.title=D2.title;
document.getElementById('t').textContent=D2.title;
function cookies(){$('ck').textContent=document.cookie?document.cookie.split('; ').join('\n'):T('empty');}
$('cs').onclick=()=>{if($('cv').value.includes('=')){document.cookie=$('cv').value+'; path=/';$('cv').value='';cookies();}};
$('cc').onclick=()=>{document.cookie.split('; ').forEach(c=>{const n=c.split('=')[0];
if(n)document.cookie=n+'=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';});cookies();};
function el(tag,cls,txt){const e=document.createElement(tag);if(cls)e.className=cls;
if(txt!==undefined)e.textContent=txt;return e;}
function card(e){
  const c=el('div','card'),r=el('div','row'),m=el('span','m '+e.method,e.method);
  const p=el('input');p.value=e.path;p.spellcheck=false;
  const go=el('button',null,T('send'));
  r.append(m,p,go);c.append(r);
  let ta=null;
  if(e.method!=='GET'){ta=el('textarea');ta.placeholder=T('body_ph');ta.spellcheck=false;c.append(ta);}
  const pl=e.presets[lang]||[];
  if(pl.length){
    const pr=el('div','pre');pr.append(el('span','tag',T('presets')));
    pl.forEach(([label,val])=>{const b=el('button','s',label);
      b.onclick=()=>{if(typeof val==='string'){p.value=val.startsWith('/')?val:e.path.replace(/\?.*/,'')+val;}
        else if(ta)ta.value=JSON.stringify(val,null,2);};
      pr.append(b);});
    c.append(pr);
  }
  if(e.method==='GET'){const a=el('a',null,T('newtab'));a.target='_blank';
    a.onclick=()=>{a.href=p.value;};a.href=p.value;
    const w=el('div','hint');w.append(a);c.append(w);}
  go.onclick=async()=>{
    const o={method:e.method,credentials:'same-origin',headers:{}};
    if(ta&&ta.value.trim()){o.headers['Content-Type']='application/json';o.body=ta.value;}
    const t0=performance.now();
    delete $('st').dataset.init;
    try{
      const res=await fetch(p.value,o),txt=await res.text();
      let shown=txt;try{shown=JSON.stringify(JSON.parse(txt),null,2);}catch(_){}
      last={status:res.status,statusText:res.statusText,ms:Math.round(performance.now()-t0),
        ok:res.ok,shown:shown,ct:res.headers.get('content-type'),
        redirected:res.redirected,url:res.url};
    }catch(err){last={err:String(err)};}
    showLast();
    cookies();
  };
  return c;
}
let last=null;
function showLast(){
  if(!last)return;
  if(last.err!==undefined){$('st').textContent=T('neterr')+last.err;$('st').className='bad';$('body').textContent='';return;}
  $('st').textContent=last.status+' '+last.statusText+'  ·  '+last.ms+T('ms');
  $('st').className=last.ok?'ok':'bad';
  $('body').textContent=last.shown||T('empty_body');
  $('hd').textContent='Content-Type: '+(last.ct||'—')+(last.redirected?T('redir')+last.url:'');
}
function render(){
  const box=$('eps');box.querySelectorAll('.card,.hint,.tag2').forEach(n=>n.remove());
  D2.endpoints.filter(e=>!e.helper).forEach(e=>box.append(card(e)));
  const hs=D2.endpoints.filter(e=>e.helper);
  if(hs.length){
    const h=el('h2',null,T('helpers'));h.className='tag2';h.style.marginTop='18px';
    h.id='hh';box.append(h);
    box.append(el('div','hint',T('helpers_hint')));
    hs.forEach(e=>box.append(card(e)));
  }
}
function applyLang(){
  document.documentElement.lang=lang;
  $('n').textContent=D2.notes[lang]||'';
  $('h-eps').textContent=T('eps');$('h-out').textContent=T('out');$('h-ck').textContent=T('ck');
  $('cv').placeholder=T('cv');$('cs').textContent=T('set');$('cc').textContent=T('clear');
  $('ck-hint').textContent=T('ck_hint');
  if($('st').dataset.init)$('st').textContent=T('send_left');
  document.querySelectorAll('#lg button').forEach(b=>b.classList.toggle('on',b.dataset.l===lang));
  showLast();render();cookies();
}
if(D2.langs.length>1){
  $('lg').hidden=false;
  document.querySelectorAll('#lg button').forEach(b=>{b.onclick=()=>{
    lang=b.dataset.l;try{localStorage.setItem('lab_lang',lang);}catch(_){}
    applyLang();};});
}
applyLang();
</script></body></html>"""
