"""
Веб-портал лабы A01: корпоративный HR-портал «TestLab HR» (страница "/").

Это учебная витрина, а НЕ часть уязвимости: она показывает уязвимость так,
как её видит обычный пользователь, и работает поверх тех же JSON-эндпоинтов
(/login, /me, /api/notes, /admin/users...). Логика доступа живёт только в
app.py; портал одинаков в vulnerable и fixed (файл побайтно один и тот же),
различается лишь параметр variant.

В браузере адрес "/" открывает портал; curl/Postman получают прежний
JSON-ответ "/". Старая консоль эндпоинтов остаётся на /ui (вкладка Raw API
в панели лабы). Языки: английский (по умолчанию), русский, узбекский;
выбор общий с /ui (?lang=ru, localStorage["lab_lang"]).

Панель лабы (кнопка Lab в правом нижнем углу): задания, которые отмечаются
сами, подсказки и журнал запросов портала.
"""
import json

from flask import Response, request


def register_portal(app, variant):
    """variant: "vulnerable" или "fixed". Вызывать ДО register_ui, чтобы
    "/" для браузера открывал портал, а не перенаправлял на /ui."""
    data = json.dumps({"variant": variant}).replace("</", "<\\/")
    page = _PAGE.replace("__DATA__", data)

    @app.before_request
    def _portal_index():
        if (request.path == "/" and request.method == "GET"
                and "text/html" in request.headers.get("Accept", "")):
            return Response(page, mimetype="text/html")


_PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TestLab HR</title>
<style>
:root{--bg:#f5f7fb;--card:#fff;--fg:#121a2b;--mut:#6b778c;--line:#e5e9f0;--acc:#2f6fed;
--acc-soft:#eaf1ff;--side:#121a2b;--side-fg:#aeb8cc;--side-hover:#1c2640;--ok:#12805c;
--ok-soft:#e3f5ec;--bad:#c2362b;--bad-soft:#fdecea;--code:#eef1f6;
--c-blue:#eaf1ff;--c-green:#e6f6ee;--c-purple:#f0ebff;--c-gray:#f1f3f6;
--i-blue:#2f6fed;--i-green:#12805c;--i-purple:#7a4de0;--i-gray:#5b6577;
--shadow:0 1px 2px rgba(18,26,43,.05)}
@media (prefers-color-scheme:dark){:root{--bg:#0e131d;--card:#161d2b;--fg:#e8ecf4;--mut:#96a3b8;
--line:#242e40;--acc:#6b9bff;--acc-soft:#1b2a4a;--side:#0a0f18;--side-hover:#141c2c;
--ok:#3ecf9a;--ok-soft:#10301f;--bad:#ff7b6f;--bad-soft:#3a1816;--code:#10151f;
--c-blue:#17233f;--c-green:#12291f;--c-purple:#241b3f;--c-gray:#1a2230;
--i-blue:#6b9bff;--i-green:#3ecf9a;--i-purple:#a98bff;--i-gray:#9aa6ba}}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
button{font:inherit;cursor:pointer}
a{color:var(--acc)}
.ico{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;flex:none}
.app{display:grid;grid-template-columns:248px minmax(0,1fr);min-height:100vh}
.side{background:var(--side);color:var(--side-fg);display:flex;flex-direction:column;padding:18px 14px;
position:sticky;top:0;height:100vh}
.brand{display:flex;align-items:center;gap:10px;color:#fff;font-weight:700;font-size:19px;padding:4px 8px 22px}
.brand .ico{width:26px;height:26px;color:#6b9bff}
.nav{display:flex;flex-direction:column;gap:4px;flex:1;overflow:auto}
.nav a,.nav button,.sidefoot a,.sidefoot button{display:flex;align-items:center;gap:12px;color:inherit;
text-decoration:none;background:none;border:0;border-radius:9px;padding:10px 12px;font-size:14.5px;text-align:left;width:100%}
.nav a:hover,.sidefoot a:hover,.sidefoot button:hover{background:var(--side-hover);color:#fff}
.nav a.on{background:var(--acc);color:#fff}
.nav .sep{height:1px;background:#243049;margin:8px 4px}
.sidefoot{display:flex;flex-direction:column;gap:4px;border-top:1px solid #243049;padding-top:10px}
.main{min-width:0;display:flex;flex-direction:column}
.top{display:flex;align-items:center;gap:12px;justify-content:flex-end;background:var(--card);
border-bottom:1px solid var(--line);padding:10px 28px;position:sticky;top:0;z-index:5}
.top .grow{flex:1}
.burger{display:none;background:none;border:0;color:var(--fg);padding:6px}
.lg{display:flex;gap:4px}
.lg button{background:var(--code);color:var(--fg);border:1px solid var(--line);border-radius:7px;
padding:3px 9px;font-size:12px;font-weight:600}
.lg button.on{background:var(--acc);border-color:var(--acc);color:#fff}
.bell{position:relative;background:none;border:0;color:var(--mut);padding:6px}
.bell i{position:absolute;top:5px;right:6px;width:8px;height:8px;border-radius:50%;background:var(--acc)}
.who{display:flex;align-items:center;gap:10px}
.who b{display:block;font-size:14px;line-height:1.2}.who span{font-size:12px;color:var(--mut)}
.av{width:38px;height:38px;border-radius:50%;background:var(--acc-soft);color:var(--acc);display:grid;
place-items:center;font-weight:700;font-size:13px;flex:none}
.av.lg2{width:64px;height:64px;font-size:20px}
.page{padding:32px 36px 90px;max-width:1180px;width:100%}
h1{font-size:34px;line-height:1.15;margin:0 0 10px;letter-spacing:-.01em}
h2{font-size:20px;margin:0 0 6px}
.sub{color:var(--mut);margin:0 0 24px}
.hero{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:24px;align-items:center;margin-bottom:22px}
.hero h1{font-size:38px}
.brandcard{position:relative;overflow:hidden;border-radius:16px;padding:22px 22px 26px;
background:linear-gradient(135deg,var(--c-blue),var(--card));border:1px solid var(--line);min-height:128px}
.brandcard .ico{width:30px;height:30px;color:var(--acc)}
.brandcard b{display:block;font-size:18px;margin-top:6px}.brandcard span{color:var(--mut);font-size:13px}
.brandcard:after{content:"";position:absolute;right:-30px;bottom:-60px;width:190px;height:140px;border-radius:50%;
background:var(--acc);opacity:.10}
.quick{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:22px}
.qc{display:block;text-decoration:none;color:var(--fg);border-radius:14px;padding:16px;border:1px solid var(--line);
position:relative;min-height:118px}
.qc .ico{width:24px;height:24px}
.qc b{display:block;margin-top:14px;font-size:15px}.qc span{display:block;color:var(--mut);font-size:12.5px;margin-top:2px;max-width:78%}
.qc .go{position:absolute;right:14px;bottom:16px;width:18px;height:18px;color:var(--acc)}
.qc.blue{background:var(--c-blue)}.qc.blue>.ico:first-child{color:var(--i-blue)}
.qc.green{background:var(--c-green)}.qc.green>.ico:first-child{color:var(--i-green)}
.qc.purple{background:var(--c-purple)}.qc.purple>.ico:first-child{color:var(--i-purple)}
.qc.gray{background:var(--c-gray)}.qc.gray>.ico:first-child{color:var(--i-gray)}
.two{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:18px;margin-bottom:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px 20px;box-shadow:var(--shadow)}
.card>.hd{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.card>.hd h2{font-size:15.5px;margin:0;display:flex;align-items:center;gap:8px;flex:1}
.card>.hd .ico{color:var(--mut)}
.card>.hd a{font-size:12.5px;text-decoration:none}
.item{display:flex;align-items:center;gap:14px;padding:12px 0;border-top:1px solid var(--line)}
.item:first-of-type{border-top:0}
.date{width:46px;height:50px;border-radius:10px;background:var(--code);display:grid;place-items:center;
text-align:center;font-size:11px;color:var(--mut);line-height:1.1;flex:none}
.date b{display:block;font-size:19px;color:var(--fg)}
.item .t{font-weight:600;font-size:14.5px}
.item .m{display:flex;gap:6px;align-items:center;color:var(--mut);font-size:12.5px;margin-top:2px}
.item .m .ico{width:14px;height:14px}
.item .grow{flex:1;min-width:0}
.thumb{width:62px;height:46px;border-radius:8px;display:grid;place-items:center;color:#fff;flex:none}
.thumb.a{background:linear-gradient(135deg,#2f6fed,#7a4de0)}.thumb.b{background:linear-gradient(135deg,#12805c,#2f6fed)}
.thumb.c{background:linear-gradient(135deg,#c26a1a,#c2362b)}
.strip{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.strip .cell{display:flex;align-items:center;gap:10px;padding:0 18px;border-left:1px solid var(--line)}
.strip .cell .ico{color:var(--mut)}.strip small{display:block;color:var(--mut);font-size:12px}
.strip .grow{flex:1}
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--acc);color:#fff;border:1px solid var(--acc);
border-radius:9px;padding:8px 16px;font-weight:600;font-size:14px;text-decoration:none}
.btn.ghost{background:var(--card);color:var(--fg);border-color:var(--line)}
.btn .ico{width:16px;height:16px}
.chip{display:inline-block;background:var(--code);border-radius:999px;padding:2px 10px;font-size:12px;color:var(--mut)}
.chip.ok{background:var(--ok-soft);color:var(--ok)}.chip.bad{background:var(--bad-soft);color:var(--bad)}
.field{display:block;margin-bottom:14px}.field span{display:block;font-size:13px;color:var(--mut);margin-bottom:5px}
input[type=text],input[type=password],input[type=search]{width:100%;background:var(--card);color:var(--fg);
border:1px solid var(--line);border-radius:9px;padding:10px 12px;font:inherit}
input:focus,button:focus-visible,a:focus-visible{outline:2px solid var(--acc);outline-offset:1px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}
.emp{display:flex;gap:14px;align-items:center}
.emp b{display:block}.emp small{color:var(--mut);display:block}
.rq{display:flex;align-items:center;gap:14px;padding:14px 0;border-top:1px solid var(--line)}
.rq:first-of-type{border-top:0}
.rq .ic{width:40px;height:40px;border-radius:10px;background:var(--c-blue);color:var(--i-blue);display:grid;place-items:center;flex:none}
.rq .grow{flex:1;min-width:0}.rq .t{font-weight:600}.rq .x{color:var(--mut);font-size:13.5px;word-break:break-word}
.tbl{width:100%;border-collapse:collapse}.tbl th{text-align:left;font-size:12px;color:var(--mut);
text-transform:uppercase;letter-spacing:.05em;padding:8px 10px;border-bottom:1px solid var(--line)}
.tbl td{padding:10px;border-bottom:1px solid var(--line)}
.note{border-radius:12px;padding:14px 16px;margin-top:16px}
.note.ok{background:var(--ok-soft);color:var(--ok)}.note.bad{background:var(--bad-soft);color:var(--bad)}
.note code,.flag{font:13px ui-monospace,Consolas,monospace}
.state{text-align:center;padding:48px 16px}.state .ico{width:42px;height:42px;color:var(--mut)}
.state.bad .ico{color:var(--bad)}.state h2{margin-top:10px}
.state p{color:var(--mut);max-width:440px;margin:6px auto 18px}
.loginwrap{min-height:100vh;display:grid;place-items:center;padding:20px;position:relative}
.logincard{width:100%;max-width:410px;background:var(--card);border:1px solid var(--line);border-radius:18px;
padding:30px 28px;box-shadow:0 8px 30px rgba(18,26,43,.08)}
.logincard .brand{color:var(--fg);padding:0 0 14px}.logincard .brand .ico{color:var(--acc)}
.logincard .btn{width:100%;justify-content:center;padding:11px}
.demo{margin-top:20px;border-top:1px solid var(--line);padding-top:14px}
.demo small{color:var(--mut);display:block;margin-bottom:8px}
.demo button{background:var(--code);color:var(--fg);border:1px solid var(--line);border-radius:8px;
padding:5px 10px;font-size:12.5px;margin:0 6px 6px 0;font-family:ui-monospace,Consolas,monospace}
.err{color:var(--bad);font-size:13.5px;margin:0 0 12px;min-height:1.2em}
.loginlang{position:absolute;top:16px;right:20px}
.fab{position:fixed;right:20px;bottom:20px;z-index:20;display:flex;align-items:center;gap:8px;background:var(--fg);
color:var(--bg);border:0;border-radius:999px;padding:11px 18px;font-weight:700;box-shadow:0 6px 20px rgba(0,0,0,.25)}
.fab .ico{width:18px;height:18px}
.drawer{position:fixed;top:0;right:0;bottom:0;width:min(400px,100vw);background:var(--card);
border-left:1px solid var(--line);box-shadow:-8px 0 30px rgba(0,0,0,.18);z-index:30;display:flex;flex-direction:column}
.drawer[hidden]{display:none}
.dh{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid var(--line)}
.dh h2{margin:0;font-size:16px;flex:1}
.dh button{background:none;border:0;color:var(--mut);padding:4px}
.tabs{display:flex;gap:4px;padding:8px 12px 0;border-bottom:1px solid var(--line)}
.tabs button{background:none;border:0;border-bottom:2px solid transparent;color:var(--mut);padding:8px 10px;font-weight:600;font-size:13.5px}
.tabs button.on{color:var(--acc);border-color:var(--acc)}
.db{flex:1;overflow:auto;padding:14px 16px}
.db .mut{color:var(--mut);font-size:13px}
.task{display:flex;gap:10px;align-items:flex-start;padding:9px 0}
.task .dot{width:20px;height:20px;border-radius:50%;border:2px solid var(--line);display:grid;place-items:center;flex:none;margin-top:1px}
.task.done .dot{background:var(--ok);border-color:var(--ok);color:#fff}
.task .dot .ico{width:12px;height:12px;stroke-width:3}
.task.done span{color:var(--mut);text-decoration:line-through}
.bar{height:6px;background:var(--code);border-radius:99px;margin:6px 0 10px;overflow:hidden}.bar i{display:block;height:100%;background:var(--ok)}
.pills{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 14px}
.pills button{background:var(--code);color:var(--fg);border:1px solid var(--line);border-radius:8px;padding:5px 10px;font-size:12.5px}
.links{display:flex;flex-direction:column;gap:6px;margin-top:6px;font-size:14px}
details{border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin-bottom:8px}
details summary{cursor:pointer;font-weight:600;font-size:14px}details p{margin:8px 0 0;font-size:14px}
.lg1{border:1px solid var(--line);border-radius:10px;margin-bottom:8px;overflow:hidden}
.lg1>button{display:flex;gap:8px;align-items:center;width:100%;background:none;border:0;color:var(--fg);padding:8px 10px;text-align:left}
.lg1 .mm{font:600 11px ui-monospace,Consolas,monospace;color:var(--mut);min-width:40px}
.lg1 .pp{flex:1;font:12.5px ui-monospace,Consolas,monospace;word-break:break-all}
.lg1 pre{margin:0;padding:10px;background:var(--code);font:12px/1.45 ui-monospace,Consolas,monospace;white-space:pre-wrap;
word-break:break-word;max-height:220px;overflow:auto}
.foot{font-size:12px;color:var(--mut);margin-top:16px}
@media (max-width:1000px){.quick{grid-template-columns:repeat(2,minmax(0,1fr))}.two,.hero{grid-template-columns:1fr}}
@media (max-width:860px){
.app{grid-template-columns:1fr}
.side{position:fixed;left:0;top:0;bottom:0;width:260px;z-index:40;transform:translateX(-100%);transition:transform .2s}
.side.open{transform:none}
.shade{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:35}
.burger{display:block;margin-right:auto}
.page{padding:22px 16px 90px}h1,.hero h1{font-size:28px}
.top{padding:10px 14px}.who div{display:none}
.strip .cell{border-left:0;padding:0}}
</style></head><body>
<div id="root"></div>
<noscript>JavaScript is required.</noscript>
<script id="d" type="application/json">__DATA__</script>
<script>
"use strict";
const CFG=JSON.parse(document.getElementById('d').textContent);
const VARIANT=CFG.variant;
const $=(i)=>document.getElementById(i);

/* ---------- иконки ---------- */
const ICONS={
home:'<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/>',
users:'<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><path d="M16 5.2a3 3 0 010 5.6M18 14.4c1.9.8 3 2.6 3 5.6"/>',
file:'<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/>',
calendar:'<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
docs:'<path d="M6 3h8l4 4v14H6z"/><path d="M9 12h6M9 16h6"/>',
poll:'<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 12l3 3 5-6"/>',
book:'<path d="M5 4h12a2 2 0 012 2v14H7a2 2 0 01-2-2z"/><path d="M5 18a2 2 0 012-2h12"/>',
gear:'<circle cx="12" cy="12" r="3"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M18.7 5.3l-2.1 2.1M7.4 16.6l-2.1 2.1"/>',
shield:'<path d="M12 3l8 3v6c0 4.5-3.2 8-8 9-4.8-1-8-4.5-8-9V6z"/>',
bell:'<path d="M6 16V11a6 6 0 1112 0v5l2 2H4z"/><path d="M10 21h4"/>',
flask:'<path d="M9 3h6M10 3v6L4.5 19a1.5 1.5 0 001.3 2.2h12.4a1.5 1.5 0 001.3-2.2L14 9V3"/><path d="M7.5 15h9"/>',
arrow:'<path d="M5 12h14M13 6l6 6-6 6"/>',
clock:'<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
pin:'<path d="M12 21s7-6.2 7-11.5a7 7 0 10-14 0C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
menu:'<path d="M4 7h16M4 12h16M4 17h16"/>',
logout:'<path d="M10 4H5v16h5M15 8l4 4-4 4M19 12H9"/>',
building:'<rect x="5" y="3" width="14" height="18" rx="1.5"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M9 15h2M13 15h2"/>',
briefcase:'<rect x="3.5" y="7" width="17" height="12" rx="2"/><path d="M9 7V5h6v2M3.5 12h17"/>',
lock:'<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 018 0v2.5"/>',
search:'<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4 4"/>',
check:'<path d="M5 12.5l4.5 4.5L19 7.5"/>',
x:'<path d="M6 6l12 12M18 6L6 18"/>',
megaphone:'<path d="M4 10v4h3l7 4V6L7 10z"/><path d="M17 9a4 4 0 010 6"/>',
question:'<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 114 2c-.9.6-1.5 1.1-1.5 2.3M12 17h.01"/>'
};
function ico(name,cls){
  const s=document.createElementNS('http://www.w3.org/2000/svg','svg');
  s.setAttribute('viewBox','0 0 24 24');s.setAttribute('class','ico'+(cls?' '+cls:''));
  s.setAttribute('aria-hidden','true');s.innerHTML=ICONS[name]||'';return s;
}
function el(tag,cls,...kids){
  const e=document.createElement(tag);if(cls)e.className=cls;
  for(const k of kids.flat()){if(k==null||k===false)continue;
    e.append(k.nodeType?k:document.createTextNode(String(k)));}
  return e;
}

/* ---------- тексты (EN / RU / UZ) ---------- */
const I={
en:{
brand:'TestLab HR',tagline:'Growing people. Building the future.',
nav_home:'Home',nav_employees:'Employees',nav_requests:'Requests',nav_calendar:'Calendar',
nav_docs:'Documents',nav_polls:'Polls',nav_kb:'Knowledge base',nav_admin:'Administration',
nav_settings:'Settings',signout:'Sign out',menu:'Menu',close:'Close',loading:'Loading…',
login_title:'Sign in to TestLab HR',login_sub:'Use your corporate account.',f_user:'Username',
f_pass:'Password',btn_signin:'Sign in',demo:'Demo accounts (click to fill in)',
bad_cred:'Invalid username or password.',neterr:'Network error. Is the server running?',
welcome:'Welcome, {name}!',welcome_sub:'Your HR portal: everything you need for work in one place.',
q_requests:'Requests',q_requests_s:'Requests filed with HR',q_calendar:'Calendar',
q_calendar_s:'My meetings and events',q_docs:'Documents',q_docs_s:'Useful files and guides',
q_emp:'Employees',q_emp_s:'Search and contacts of colleagues',
upcoming:'Upcoming events',all_events:'All events',news:'News',all_news:'All news',
ev1:'Meeting with your manager',ev2:'Training: Introduction to testing',ev3:'Company meeting',
loc_online:'Online',loc_room2:'Office, meeting room 2',loc_hall:'Office, assembly hall',
m10:'Oct',m11:'Nov',news1:'Corporate training program starts',news1_d:'24 Oct 2026',
news2:'New growth opportunities at TestLab',news2_d:'18 Oct 2026',
news3:'Corporate portal updated',news3_d:'12 Oct 2026',
dept:'Department',pos:'Position',role:'Role',my_profile:'My profile',
d_qa:'QA',d_dev:'Development',d_hr:'HR',d_design:'Design',d_finance:'Finance',d_sales:'Sales',
p_qa_engineer:'QA engineer',p_developer:'Software developer',p_hr_admin:'HR administrator',
p_designer:'UI designer',p_accountant:'Accountant',p_sales_manager:'Sales manager',
role_user:'Employee',role_admin:'Administrator',
emp_title:'Employees',emp_sub:'Colleagues and their contacts.',emp_search:'Search by name or department',
emp_none:'Nobody found.',
req_title:'Requests',req_sub:'Requests you have filed with HR.',req_none:'You have no requests yet.',
req_open:'Open',req_no:'Request #{id}',back:'Back to requests',req_owner:'Filed by',
denied_title:'Access denied',denied_text:'The server refused the request (403 Forbidden).',
nf_title:'Not found',nf_text:'Nothing exists at this address (404).',
admin_title:'Administration',admin_sub:'User accounts and system information.',
admin_users:'User accounts',col_user:'Username',col_role:'Role',admin_flag:'Lab flag',
stub_title:'Not part of this lab',
stub_text:'This section is here only so the portal looks like a real one. There is nothing to find in it.',
profile_title:'My profile',
lab:'Lab',panel_title:'Lab panel',v_vulnerable:'vulnerable version',v_fixed:'fixed version',
tab_tasks:'Tasks',tab_hints:'Hints',tab_log:'Requests',
tasks_note:'A task ticks itself when the matching request goes through.',
signin_as:'Sign in as',raw:'Raw API console',other_fixed:'Open the fixed version',
other_vulnerable:'Open the vulnerable version',
hint:'Hint {n}',log_empty:'No requests yet. Use the portal and they will show up here.',
log_clear:'Clear',flags_seen:'Flags seen',
foot:'Lab only: this portal is vulnerable on purpose. Do not expose it to the internet.',
tk_vulnerable:['Sign in as alice','Read the admin’s request (it holds a flag)','Open the Administration page without being an admin'],
tk_fixed:['Sign in as alice','Try to open request #3: the server must refuse','Try the Administration page as alice: the server must refuse','Sign in as admin: the Administration page must still work'],
hints:['Open “Requests”. What numbers do your requests have, and where do they show up in the address bar?','What happens if you put another number into the address of a request?','The “Administration” menu item is hidden from you. Does the server care whether you can see the menu?']
},
ru:{
brand:'TestLab HR',tagline:'Развиваем людей. Создаём будущее.',
nav_home:'Главная',nav_employees:'Сотрудники',nav_requests:'Заявки',nav_calendar:'Календарь',
nav_docs:'Документы',nav_polls:'Опросы',nav_kb:'База знаний',nav_admin:'Администрирование',
nav_settings:'Настройки',signout:'Выйти',menu:'Меню',close:'Закрыть',loading:'Загрузка…',
login_title:'Вход в TestLab HR',login_sub:'Используйте корпоративную учётную запись.',f_user:'Логин',
f_pass:'Пароль',btn_signin:'Войти',demo:'Демо-аккаунты (нажмите, чтобы подставить)',
bad_cred:'Неверный логин или пароль.',neterr:'Ошибка сети. Сервер запущен?',
welcome:'Добро пожаловать, {name}!',welcome_sub:'Твой HR-портал: всё, что нужно для работы, в одном месте.',
q_requests:'Заявки',q_requests_s:'Заявки, поданные в HR',q_calendar:'Календарь',
q_calendar_s:'Мои встречи и события',q_docs:'Документы',q_docs_s:'Полезные файлы и инструкции',
q_emp:'Сотрудники',q_emp_s:'Поиск и контакты коллег',
upcoming:'Ближайшие события',all_events:'Все события',news:'Новости',all_news:'Все новости',
ev1:'Встреча с руководителем',ev2:'Обучение: Введение в тестирование',ev3:'Корпоративное собрание',
loc_online:'Онлайн',loc_room2:'Офис, переговорная 2',loc_hall:'Офис, актовый зал',
m10:'Окт',m11:'Ноя',news1:'Стартует программа корпоративного обучения',news1_d:'24 окт 2026',
news2:'Новые возможности для развития в TestLab',news2_d:'18 окт 2026',
news3:'Обновлён корпоративный портал',news3_d:'12 окт 2026',
dept:'Отдел',pos:'Должность',role:'Роль',my_profile:'Мой профиль',
d_qa:'QA',d_dev:'Разработка',d_hr:'HR',d_design:'Дизайн',d_finance:'Финансы',d_sales:'Продажи',
p_qa_engineer:'Инженер по тестированию',p_developer:'Разработчик',p_hr_admin:'HR-администратор',
p_designer:'UI-дизайнер',p_accountant:'Бухгалтер',p_sales_manager:'Менеджер по продажам',
role_user:'Сотрудник',role_admin:'Администратор',
emp_title:'Сотрудники',emp_sub:'Коллеги и их контакты.',emp_search:'Поиск по имени или отделу',
emp_none:'Никого не найдено.',
req_title:'Заявки',req_sub:'Заявки, которые вы подали в HR.',req_none:'У вас пока нет заявок.',
req_open:'Открыть',req_no:'Заявка №{id}',back:'К списку заявок',req_owner:'Подал(а)',
denied_title:'Доступ запрещён',denied_text:'Сервер отказал в запросе (403 Forbidden).',
nf_title:'Не найдено',nf_text:'По этому адресу ничего нет (404).',
admin_title:'Администрирование',admin_sub:'Учётные записи пользователей и сведения о системе.',
admin_users:'Учётные записи',col_user:'Логин',col_role:'Роль',admin_flag:'Флаг лабы',
stub_title:'Не входит в лабу',
stub_text:'Этот раздел нужен только для того, чтобы портал выглядел как настоящий. Искать здесь нечего.',
profile_title:'Мой профиль',
lab:'Лаба',panel_title:'Панель лабы',v_vulnerable:'уязвимая версия',v_fixed:'исправленная версия',
tab_tasks:'Задания',tab_hints:'Подсказки',tab_log:'Запросы',
tasks_note:'Задание отмечается само, когда проходит нужный запрос.',
signin_as:'Войти как',raw:'Консоль Raw API',other_fixed:'Открыть исправленную версию',
other_vulnerable:'Открыть уязвимую версию',
hint:'Подсказка {n}',log_empty:'Запросов пока нет. Пользуйтесь порталом, и они появятся здесь.',
log_clear:'Очистить',flags_seen:'Найденные флаги',
foot:'Только для лабы: портал уязвим намеренно. Не публикуйте его в интернете.',
tk_vulnerable:['Войти как alice','Прочитать заявку админа (в ней флаг)','Открыть страницу «Администрирование», не будучи админом'],
tk_fixed:['Войти как alice','Попробовать открыть заявку №3: сервер должен отказать','Попробовать страницу «Администрирование» под alice: сервер должен отказать','Войти как admin: страница «Администрирование» должна по-прежнему работать'],
hints:['Откройте «Заявки». Какие номера у ваших заявок и где они видны в адресной строке?','Что будет, если подставить в адрес заявки другой номер?','Пункт меню «Администрирование» от вас скрыт. Интересует ли сервер, видите ли вы это меню?']
},
uz:{
brand:'TestLab HR',tagline:'Odamlarni rivojlantiramiz. Kelajakni yaratamiz.',
nav_home:'Bosh sahifa',nav_employees:'Xodimlar',nav_requests:'Arizalar',nav_calendar:'Kalendar',
nav_docs:'Hujjatlar',nav_polls:'Soʻrovnomalar',nav_kb:'Bilimlar bazasi',nav_admin:'Boshqaruv',
nav_settings:'Sozlamalar',signout:'Chiqish',menu:'Menyu',close:'Yopish',loading:'Yuklanmoqda…',
login_title:'TestLab HR tizimiga kirish',login_sub:'Korporativ akkauntingizdan foydalaning.',
f_user:'Foydalanuvchi nomi',f_pass:'Parol',btn_signin:'Kirish',
demo:'Demo akkauntlar (toʻldirish uchun bosing)',bad_cred:'Foydalanuvchi nomi yoki parol notoʻgʻri.',
neterr:'Tarmoq xatosi. Server ishlayaptimi?',
welcome:'Xush kelibsiz, {name}!',welcome_sub:'Sizning HR portalingiz: ish uchun kerak boʻlgan hamma narsa bir joyda.',
q_requests:'Arizalar',q_requests_s:'HRga yuborilgan arizalar',q_calendar:'Kalendar',
q_calendar_s:'Mening uchrashuvlarim va tadbirlarim',q_docs:'Hujjatlar',q_docs_s:'Foydali fayllar va yoʻriqnomalar',
q_emp:'Xodimlar',q_emp_s:'Hamkasblarni qidirish va kontaktlar',
upcoming:'Yaqin tadbirlar',all_events:'Barcha tadbirlar',news:'Yangiliklar',all_news:'Barcha yangiliklar',
ev1:'Rahbar bilan uchrashuv',ev2:'Oʻqitish: Testlashga kirish',ev3:'Korporativ yigʻilish',
loc_online:'Onlayn',loc_room2:'Ofis, 2-uchrashuv xonasi',loc_hall:'Ofis, aktlar zali',
m10:'Okt',m11:'Noy',news1:'Korporativ oʻqitish dasturi boshlanmoqda',news1_d:'24.10.2026',
news2:'TestLabda rivojlanishning yangi imkoniyatlari',news2_d:'18.10.2026',
news3:'Korporativ portal yangilandi',news3_d:'12.10.2026',
dept:'Boʻlim',pos:'Lavozim',role:'Rol',my_profile:'Mening profilim',
d_qa:'QA',d_dev:'Dasturlash',d_hr:'HR',d_design:'Dizayn',d_finance:'Moliya',d_sales:'Savdo',
p_qa_engineer:'QA muhandisi',p_developer:'Dasturchi',p_hr_admin:'HR administratori',
p_designer:'UI dizayner',p_accountant:'Buxgalter',p_sales_manager:'Savdo menejeri',
role_user:'Xodim',role_admin:'Administrator',
emp_title:'Xodimlar',emp_sub:'Hamkasblar va ularning kontaktlari.',emp_search:'Ism yoki boʻlim boʻyicha qidirish',
emp_none:'Hech kim topilmadi.',
req_title:'Arizalar',req_sub:'HRga yuborgan arizalaringiz.',req_none:'Sizda hali arizalar yoʻq.',
req_open:'Ochish',req_no:'{id}-ariza',back:'Arizalar roʻyxatiga',req_owner:'Yuboruvchi',
denied_title:'Kirish taqiqlandi',denied_text:'Server soʻrovni rad etdi (403 Forbidden).',
nf_title:'Topilmadi',nf_text:'Bu manzilda hech narsa yoʻq (404).',
admin_title:'Boshqaruv',admin_sub:'Foydalanuvchi akkauntlari va tizim maʼlumotlari.',
admin_users:'Foydalanuvchi akkauntlari',col_user:'Foydalanuvchi nomi',col_role:'Rol',admin_flag:'Laboratoriya flagi',
stub_title:'Laboratoriyaga kirmaydi',
stub_text:'Bu boʻlim portal haqiqiy saytga oʻxshab koʻrinishi uchun qoʻyilgan. Bu yerda topiladigan narsa yoʻq.',
profile_title:'Mening profilim',
lab:'Laboratoriya',panel_title:'Laboratoriya paneli',v_vulnerable:'zaif versiya',v_fixed:'tuzatilgan versiya',
tab_tasks:'Topshiriqlar',tab_hints:'Maslahatlar',tab_log:'Soʻrovlar',
tasks_note:'Mos soʻrov oʻtganda topshiriq oʻzi belgilanadi.',
signin_as:'Kirish:',raw:'Raw API konsoli',other_fixed:'Tuzatilgan versiyani ochish',
other_vulnerable:'Zaif versiyani ochish',
hint:'{n}-maslahat',log_empty:'Hozircha soʻrovlar yoʻq. Portaldan foydalaning, ular shu yerda paydo boʻladi.',
log_clear:'Tozalash',flags_seen:'Topilgan flaglar',
foot:'Faqat laboratoriya uchun: portal ataylab zaif qilingan. Uni internetga chiqarmang.',
tk_vulnerable:['alice sifatida kiring','Adminning arizasini oʻqing (unda flag bor)','Admin boʻlmasdan «Boshqaruv» sahifasini oching'],
tk_fixed:['alice sifatida kiring','3-arizani ochib koʻring: server rad etishi kerak','«Boshqaruv» sahifasini alice sifatida ochib koʻring: server rad etishi kerak','admin sifatida kiring: «Boshqaruv» sahifasi avvalgidek ishlashi kerak'],
hints:['«Arizalar» boʻlimini oching. Arizalaringizning raqamlari qanday va ular manzil qatorida qayerda koʻrinadi?','Ariza manziliga boshqa raqam qoʻysangiz nima boʻladi?','«Boshqaruv» menyu bandi sizdan yashirilgan. Server menyuni koʻrishingizga eʼtibor beradimi?']
}};
const LANGS=['en','ru','uz'];
function pickLang(){
  let l=null;
  try{l=new URLSearchParams(location.search).get('lang')||localStorage.getItem('lab_lang');}catch(_){}
  if(!l){try{if(/^uz/i.test(navigator.language||''))l='uz';}catch(_){}}
  return LANGS.includes(l)?l:'en';
}
let lang=pickLang();
function t(k,v){
  let s=(I[lang]&&I[lang][k]!==undefined)?I[lang][k]:(I.en[k]!==undefined?I.en[k]:k);
  if(v)for(const x in v)s=s.replace('{'+x+'}',v[x]);
  return s;
}
const tl=(k)=>(I[lang][k]||I.en[k]);

/* ---------- состояние ---------- */
const KEY='lab_a01_'+VARIANT;
let ME=null,route=parseHash(),panelOpen=false,panelTab='tasks',navOpen=false,renderId=0;
const LOG=[];
let DONE=new Set(),FLAGS=new Set();
try{const s=JSON.parse(localStorage.getItem(KEY)||'{}');DONE=new Set(s.done||[]);FLAGS=new Set(s.flags||[]);}catch(_){}
function save(){try{localStorage.setItem(KEY,JSON.stringify({done:[...DONE],flags:[...FLAGS]}));}catch(_){}}

/* задания: test(e) получает запись журнала, ME уже актуален */
const isAdmin=()=>ME&&ME.role==='admin';
const TASKS={
vulnerable:[
 {id:'v1',test:e=>e.path==='/login'&&e.status===200&&e.data&&e.data.user==='alice'},
 {id:'v2',test:e=>e.path==='/api/notes/3'&&e.status===200&&e.text.includes('FLAG{')&&ME&&!isAdmin()},
 {id:'v3',test:e=>e.path==='/admin/users'&&e.status===200&&ME&&!isAdmin()}],
fixed:[
 {id:'f1',test:e=>e.path==='/login'&&e.status===200&&e.data&&e.data.user==='alice'},
 {id:'f2',test:e=>e.path==='/api/notes/3'&&e.status===403&&ME&&!isAdmin()},
 {id:'f3',test:e=>e.path==='/admin/users'&&e.status===403&&ME&&!isAdmin()},
 {id:'f4',test:e=>e.path==='/admin/users'&&e.status===200&&isAdmin()}]
}[VARIANT];

/* ---------- запросы к API (с журналом) ---------- */
async function api(method,path,body,quiet){
  const o={method,credentials:'same-origin',headers:{}};
  if(body!==undefined){o.headers['Content-Type']='application/json';o.body=JSON.stringify(body);}
  const e={method,path,status:0,text:'',data:null,ts:Date.now()};
  try{const r=await fetch(path,o);e.status=r.status;e.text=await r.text();
    try{e.data=JSON.parse(e.text);}catch(_){}}
  catch(err){e.text=String(err);}
  e.ok=e.status>=200&&e.status<300;
  if(!quiet){
    LOG.unshift(e);LOG.length=Math.min(LOG.length,30);
    (e.text.match(/FLAG\{[^}\s]+\}/g)||[]).forEach(f=>FLAGS.add(f));
    TASKS.forEach(k=>{if(!DONE.has(k.id)&&k.test(e))DONE.add(k.id);});
    save();mountPanel();
  }
  return e;
}
async function loadMe(){
  const r=await api('GET','/me',undefined,true);
  ME=r.ok&&r.data?r.data:null;return ME;
}

/* ---------- роутинг ---------- */
function parseHash(){
  const h=(location.hash||'#/home').replace(/^#\/?/,'');
  const p=h.split('/');return {name:p[0]||'home',arg:p[1]||null};
}
window.addEventListener('hashchange',()=>{route=parseHash();navOpen=false;render();window.scrollTo(0,0);});
const go=(h)=>{if(location.hash===h)render();else location.hash=h;};

/* ---------- мелкие помощники ---------- */
const initials=(n)=>(n||'?').split(/\s+/).slice(0,2).map(s=>s[0]).join('').toUpperCase();
const firstName=(n)=>(n||'').split(/\s+/)[0];
function avatar(n,big){return el('div','av'+(big?' lg2':''),initials(n));}
function langSwitch(){
  const d=el('div','lg');
  LANGS.forEach(l=>{const b=el('button',l===lang?'on':'',l.toUpperCase());
    b.onclick=()=>{lang=l;try{localStorage.setItem('lab_lang',l);}catch(_){}render();};d.append(b);});
  return d;
}
function stateBox(kind,icon,title,text,back){
  const s=el('div','state card '+kind,ico(icon),el('h2',null,title),el('p',null,text));
  if(back)s.append(Object.assign(el('a','btn ghost',back[0]),{href:back[1]}));

  return s;
}
const EVENTS=[{d:'28',m:'m10',time:'10:00 – 10:30',t:'ev1',loc:'loc_online'},
 {d:'30',m:'m10',time:'14:00 – 16:00',t:'ev2',loc:'loc_room2'},
 {d:'02',m:'m11',time:'11:00 – 12:00',t:'ev3',loc:'loc_hall'}];
const NEWS=[{t:'news1',d:'news1_d',c:'a'},{t:'news2',d:'news2_d',c:'b'},{t:'news3',d:'news3_d',c:'c'}];
function eventRow(e){
  return el('div','item',
    el('div','date',el('div',null,el('b',null,e.d),t(e.m))),
    el('div','grow',el('div','t',t(e.t)),
      el('div','m',ico('clock'),e.time,'  ',ico('pin'),t(e.loc))),
    ico('arrow','mut'));
}

/* ---------- страницы ---------- */
function pageHome(box){
  const first=firstName(ME.name)||ME.user;
  box.append(el('div','hero',
    el('div',null,el('h1',null,t('welcome',{name:first})),el('p','sub',t('welcome_sub'))),
    el('div','brandcard',ico('flask'),el('b',null,t('brand')),el('span',null,t('tagline')))));
  const q=(cls,icon,k,h)=>{const a=el('a','qc '+cls,ico(icon),el('b',null,t(k)),el('span',null,t(k+'_s')),ico('arrow','go'));a.href=h;return a;};
  box.append(el('div','quick',q('blue','file','q_requests','#/requests'),q('green','calendar','q_calendar','#/calendar'),
    q('purple','docs','q_docs','#/documents'),q('gray','users','q_emp','#/employees')));
  const evCard=el('div','card',el('div','hd',el('h2',null,ico('calendar'),t('upcoming')),
    Object.assign(el('a',null,t('all_events')),{href:'#/calendar'})),EVENTS.map(eventRow));
  const nwCard=el('div','card',el('div','hd',el('h2',null,ico('megaphone'),t('news')),
    Object.assign(el('a',null,t('all_news')),{href:'#/home'})),
    NEWS.map(n=>el('div','item',el('div','thumb '+n.c,ico('megaphone')),
      el('div','grow',el('div','t',t(n.t)),el('div','m',t(n.d))))));
  box.append(el('div','two',evCard,nwCard));
  const me=Object.assign(el('a','btn ghost',t('my_profile'),ico('arrow')),{href:'#/profile'});
  box.append(el('div','card strip',avatar(ME.name),
    el('div','grow',el('b',null,ME.name),el('small',null,t('role_'+ME.role))),
    el('div','cell',ico('building'),el('div',null,el('small',null,t('dept')),t('d_'+ME.department))),
    el('div','cell',ico('briefcase'),el('div',null,el('small',null,t('pos')),t('p_'+ME.position))),me));
}
function pageProfile(box){
  box.append(el('h1',null,t('profile_title')),
    el('div','card emp',avatar(ME.name,true),el('div',null,el('b',null,ME.name),
      el('small',null,t('p_'+ME.position)+' · '+t('d_'+ME.department)),
      el('small',null,t('role')+': '+t('role_'+ME.role)))));
}
async function pageEmployees(box,rid){
  box.append(el('h1',null,t('emp_title')),el('p','sub',t('emp_sub')));
  const inp=el('input');inp.type='search';inp.placeholder=t('emp_search');inp.setAttribute('aria-label',t('emp_search'));
  const wrap=el('div','field',inp),list=el('div','grid');box.append(wrap,list);
  const r=await api('GET','/api/employees');
  if(rid!==renderId)return;
  if(r.status===401){ME=null;return render();}
  const all=r.ok&&Array.isArray(r.data)?r.data:[];
  const draw=()=>{
    const q=inp.value.trim().toLowerCase();list.replaceChildren();
    const rows=all.filter(e=>!q||(e.name+' '+t('d_'+e.department)).toLowerCase().includes(q));
    if(!rows.length)list.append(el('p','sub',t('emp_none')));
    rows.forEach(e=>list.append(el('div','card emp',avatar(e.name),el('div',null,el('b',null,e.name),
      el('small',null,t('p_'+e.position)),el('small',null,t('d_'+e.department)),el('small',null,e.email)))));
  };
  inp.oninput=draw;draw();
}
async function pageRequests(box,rid){
  box.append(el('h1',null,t('req_title')),el('p','sub',t('req_sub')));
  const card=el('div','card');box.append(card);
  const r=await api('GET','/api/notes');
  if(rid!==renderId)return;
  if(r.status===401){ME=null;return render();}
  const rows=r.ok&&Array.isArray(r.data)?r.data:[];
  if(!rows.length)card.append(el('p','sub',t('req_none')));
  rows.forEach(n=>{
    const a=Object.assign(el('a','btn ghost',t('req_open')),{href:'#/requests/'+n.id});
    card.append(el('div','rq',el('div','ic',ico('file')),
      el('div','grow',el('div','t',t('req_no',{id:n.id})),el('div','x',n.text)),a));
  });
}
async function pageRequest(box,rid,id){
  const back=[t('back'),'#/requests'];
  if(!/^\d+$/.test(id||'')){box.append(stateBox('','question',t('nf_title'),t('nf_text'),back));return;}
  const r=await api('GET','/api/notes/'+id);
  if(rid!==renderId)return;
  if(r.status===401){ME=null;return render();}
  if(r.status===403){box.append(stateBox('bad','lock',t('denied_title'),t('denied_text'),back));return;}
  if(!r.ok||!r.data){box.append(stateBox('','question',t('nf_title'),t('nf_text'),back));return;}
  const n=r.data;
  box.append(el('h1',null,t('req_no',{id:n.id})),
    el('div','card',el('div','rq',el('div','ic',ico('file')),
      el('div','grow',el('div','t',t('req_owner')+': '+n.owner),el('div','x',n.text)))),
    el('p',null,Object.assign(el('a',null,t('back')),{href:'#/requests'})));
}
async function pageAdmin(box,rid){
  const back=[t('nav_home'),'#/home'];
  const r=await api('GET','/admin/users');
  if(rid!==renderId)return;
  if(r.status===401){ME=null;return render();}
  if(r.status===403){box.append(stateBox('bad','lock',t('denied_title'),t('denied_text'),back));return;}
  const users=(r.data&&r.data.users)||[];
  const tb=el('table','tbl',el('thead',null,el('tr',null,el('th',null,t('col_user')),el('th',null,t('col_role')))),
    el('tbody',null,users.map(u=>el('tr',null,el('td',null,u.username),
      el('td',null,el('span','chip',t('role_'+u.role)))))));
  box.append(el('h1',null,t('admin_title')),el('p','sub',t('admin_sub')),
    el('div','card',el('div','hd',el('h2',null,ico('shield'),t('admin_users'))),tb));
  if(r.data&&r.data.flag)box.append(el('div','note ok',t('admin_flag')+': ',el('code',null,r.data.flag)));
}
function pageCalendar(box){
  box.append(el('h1',null,t('nav_calendar')),el('p','sub',t('q_calendar_s')),
    el('div','card',EVENTS.map(eventRow)));
}
function pageStub(box,key){
  box.append(el('h1',null,t(key)),stateBox('','question',t('stub_title'),t('stub_text'),[t('nav_home'),'#/home']));
}

/* ---------- каркас ---------- */
const NAV=[['home','home','nav_home'],['employees','users','nav_employees'],['requests','file','nav_requests'],
 ['calendar','calendar','nav_calendar'],['documents','docs','nav_docs'],['polls','poll','nav_polls'],['kb','book','nav_kb']];
async function doLogout(){await api('POST','/logout',undefined,true);ME=null;go('#/home');render();}
function shell(view){
  const items=NAV.slice();
  const nav=el('nav','nav');
  items.forEach(([k,ic,lbl])=>{
    const on=route.name===k||(k==='requests'&&route.name==='requests');
    const a=el('a',on?'on':'',ico(ic),t(lbl));a.href='#/'+k;nav.append(a);});
  if(isAdmin()){nav.append(el('div','sep'));
    const a=el('a',route.name==='admin'?'on':'',ico('shield'),t('nav_admin'));a.href='#/admin';nav.append(a);}
  const set=el('a',route.name==='settings'?'on':'',ico('gear'),t('nav_settings'));set.href='#/settings';
  const out=el('button',null,ico('logout'),t('signout'));out.onclick=doLogout;
  const side=el('aside','side'+(navOpen?' open':''),el('div','brand',ico('flask'),t('brand')),nav,
    el('div','sidefoot',set,out));
  const burger=el('button','burger',ico('menu'));burger.setAttribute('aria-label',t('menu'));
  burger.onclick=()=>{navOpen=!navOpen;render();};
  const bell=el('button','bell',ico('bell'),el('i'));bell.setAttribute('aria-label','notifications');
  const top=el('header','top',burger,langSwitch(),bell,
    el('div','who',avatar(ME.name),el('div',null,el('b',null,ME.name),el('span',null,t('role_'+ME.role)))));
  const main=el('div','main',top,view);
  const app=el('div','app',side,main);
  if(navOpen){const sh=el('div','shade');sh.onclick=()=>{navOpen=false;render();};app.append(sh);}
  return app;
}
function loginView(){
  const msg=el('p','err');msg.setAttribute('role','alert');
  const u=el('input');u.type='text';u.autocomplete='username';u.spellcheck=false;
  const p=el('input');p.type='password';p.autocomplete='current-password';
  const btn=el('button','btn',t('btn_signin'));btn.type='submit';
  const form=el('form',null,el('label','field',el('span',null,t('f_user')),u),
    el('label','field',el('span',null,t('f_pass')),p),msg,btn);
  form.onsubmit=async(ev)=>{ev.preventDefault();msg.textContent='';
    const r=await api('POST','/login',{username:u.value,password:p.value});
    if(r.ok){await loadMe();render();}
    else msg.textContent=r.status===401?t('bad_cred'):t('neterr');};
  const demo=el('div','demo',el('small',null,t('demo')));
  [['alice','alice123'],['bob','bob123'],['admin','Adm1n-lab-pass']].forEach(([a,b])=>{
    const c=el('button',null,a+' / '+b);c.type='button';c.onclick=()=>{u.value=a;p.value=b;p.focus();};demo.append(c);});
  return el('div','loginwrap',Object.assign(langSwitch(),{className:'lg loginlang'}),
    el('div','logincard',el('div','brand',ico('flask'),t('brand')),el('h2',null,t('login_title')),
      el('p','sub',t('login_sub')),form,demo));
}

/* ---------- панель лабы ---------- */
function otherVersion(){
  const p=location.port;
  if(p==='8001')return ['other_fixed','http://127.0.0.1:8002/'];
  if(p==='8002')return ['other_vulnerable','http://127.0.0.1:8001/'];
  return null;
}
function panelBody(){
  const b=el('div','db');
  if(panelTab==='tasks'){
    const tk=tl('tk_'+VARIANT),total=TASKS.length;
    const n=TASKS.filter(k=>DONE.has(k.id)).length;
    b.append(el('div','mut',t('tasks_note')),el('b',null,n+' / '+total),
      el('div','bar',Object.assign(el('i'),{style:'width:'+Math.round(100*n/total)+'%'})));
    TASKS.forEach((k,i)=>b.append(el('div','task'+(DONE.has(k.id)?' done':''),
      el('div','dot',DONE.has(k.id)?ico('check'):null),el('span',null,tk[i]))));
    b.append(el('div','mut',t('signin_as')));
    const pills=el('div','pills');
    [['alice','alice123'],['bob','bob123'],['admin','Adm1n-lab-pass']].forEach(([a,pw])=>{
      const x=el('button',null,a);x.onclick=async()=>{await api('POST','/login',{username:a,password:pw});await loadMe();render();};
      pills.append(x);});
    b.append(pills);
    const links=el('div','links');
    const raw=el('a',null,t('raw'));raw.href='/ui?lang='+lang;raw.target='_blank';links.append(raw);
    const o=otherVersion();if(o){const a=el('a',null,t(o[0]));a.href=o[1];links.append(a);}
    b.append(links);
  }else if(panelTab==='hints'){
    tl('hints').forEach((h,i)=>b.append(el('details',null,el('summary',null,t('hint',{n:i+1})),el('p',null,h))));
  }else{
    if(FLAGS.size){b.append(el('div','mut',t('flags_seen')));
      const f=el('div','pills');[...FLAGS].forEach(x=>f.append(el('span','chip ok flag',x)));b.append(f);}
    if(!LOG.length)b.append(el('p','mut',t('log_empty')));
    else{const c=el('button','btn ghost',t('log_clear'));c.style.marginBottom='10px';
      c.onclick=()=>{LOG.length=0;mountPanel();};b.append(c);}
    LOG.forEach(e=>{
      const pre=el('pre',null,e.text||'(empty)');pre.hidden=true;
      const head=el('button',null,el('span','mm',e.method),el('span','pp',e.path),
        el('span','chip '+(e.ok?'ok':'bad'),String(e.status||'ERR')));
      head.onclick=()=>{pre.hidden=!pre.hidden;};
      b.append(el('div','lg1',head,pre));});
  }
  b.append(el('div','foot',t('foot')));
  return b;
}
function mountPanel(){
  let w=$('panelwrap');
  if(!w){w=el('div');w.id='panelwrap';document.body.append(w);}
  w.replaceChildren();
  const fab=el('button','fab',ico('flask'),t('lab'));fab.hidden=panelOpen;
  fab.onclick=()=>{panelOpen=true;mountPanel();};
  const tabs=el('div','tabs');
  [['tasks','tab_tasks'],['hints','tab_hints'],['log','tab_log']].forEach(([k,l])=>{
    const x=el('button',panelTab===k?'on':'',t(l)+(k==='log'&&LOG.length?' ('+LOG.length+')':''));
    x.onclick=()=>{panelTab=k;mountPanel();};tabs.append(x);});
  const cl=el('button',null,ico('x'));cl.setAttribute('aria-label',t('close'));
  cl.onclick=()=>{panelOpen=false;mountPanel();};
  const d=el('aside','drawer',el('div','dh',el('h2',null,t('panel_title')),
    el('span','chip',t('v_'+VARIANT)),cl),tabs,panelBody());
  d.hidden=!panelOpen;
  w.append(fab,d);
}
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&panelOpen){panelOpen=false;mountPanel();}});

/* ---------- отрисовка ---------- */
async function render(){
  const rid=++renderId;
  document.documentElement.lang=lang;
  document.title=t('brand');
  const root=$('root');
  if(!ME){root.replaceChildren(loginView());mountPanel();return;}
  const view=el('main','page');
  root.replaceChildren(shell(view));
  mountPanel();
  const n=route.name;
  if(n==='home')pageHome(view);
  else if(n==='profile')pageProfile(view);
  else if(n==='employees')await pageEmployees(view,rid);
  else if(n==='requests')await (route.arg?pageRequest(view,rid,route.arg):pageRequests(view,rid));
  else if(n==='admin')await pageAdmin(view,rid);
  else if(n==='calendar')pageCalendar(view);
  else if(n==='documents')pageStub(view,'nav_docs');
  else if(n==='polls')pageStub(view,'nav_polls');
  else if(n==='kb')pageStub(view,'nav_kb');
  else if(n==='settings')pageStub(view,'nav_settings');
  else pageHome(view);
}
(async()=>{await loadMe();render();})();
</script></body></html>"""
