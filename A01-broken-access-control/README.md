🌐 **English** · [Русский](./README.ru.md) · [Oʻzbekcha](./README.uz.md)

# A01 — Broken Access Control

**Status:** ✅ ready

## About the lab
A corporate HR portal (**TestLab HR**) with three users (`alice`, `bob`, `admin`): employees file requests with HR and browse the staff directory, and an administrator has a separate section. Login works, but the server does not always check **who owns** a resource and **which role** the user has.

## What you will learn
- To find IDOR (swapping a resource identifier in a request)
- To tell authentication ("who are you") from authorization ("what are you allowed to do")
- To check permissions on the server on every request, following the "deny by default" principle

## Running

```bash
docker compose up --build
```

| Version | Address |
|---------|---------|
| vulnerable | http://127.0.0.1:8001 |
| fixed | http://127.0.0.1:8002 |

Without Docker:

```bash
pip install -r vulnerable/requirements.txt
python vulnerable/app.py   # http://127.0.0.1:5000
```

> ⚠️ The application is vulnerable on purpose. Run it locally only and do not expose it to the internet.

Open the address in a browser and you get the TestLab HR portal. The **Lab** button (bottom right) opens the lab panel: tasks that tick themselves, hints and a log of the portal's requests. The raw API console is at `/ui`; `curl` and Postman still get the JSON from `/`.

## Task
Test account: `alice` / `alice123`.

1. Log in as `alice` (`POST /login`, JSON with `username` and `password`).
2. Read the request that belongs to the **admin** (it hides a `FLAG{...}` flag; in the portal requests open at `#/requests/<id>`).
3. Open the admin section `/admin/users` without being an admin (in the portal: `#/admin`).
4. Repeat the same requests against the **fixed** version and make sure access is denied.
5. Compare `vulnerable/app.py` and `fixed/app.py`: the fixes are marked `FIX`.

## Hints
1. Open `GET /api/notes`: what are the `id`s of your requests?
2. What does `GET /api/notes/<id>` return if you put in someone else's `id`?
3. Which checks does the server make before `GET /admin/users`? The portal hides the menu item from you, but does that stop the server?

Full solution with spoilers: [SOLUTION.md](./SOLUTION.md)

## How to defend
- Check the resource owner and the user's role **on the server**, for every request
- Deny by default: access only where it is explicitly allowed
- Do not rely on "the user does not know the URL"
