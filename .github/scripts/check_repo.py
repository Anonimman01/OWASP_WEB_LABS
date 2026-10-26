"""Repo consistency checks: shared files must stay byte-identical, code must compile."""
import glob, hashlib, py_compile, sys

fails = []


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def same(pattern, what):
    files = sorted(glob.glob(pattern))
    sums = {f: md5(f) for f in files}
    ok = len(files) > 0 and len(set(sums.values())) == 1
    print(("ok   " if ok else "FAIL ") + f"{what}: {len(files)} files, {len(set(sums.values()))} distinct md5")
    if not ok:
        fails.append(what)
        for f, s in sums.items():
            print("     ", s, f)


# labui.py is copied verbatim into every lab (20 places)
same("A*/*/labui.py", "labui.py identical everywhere")
# A01 portal and A02 site: logic differs only in app.py
same("A01-*/*/portal.py", "A01 portal.py identical in vulnerable/fixed")
same("A02-*/*/cafe.py", "A02 cafe.py identical in vulnerable/fixed")

# every Dockerfile must make the app reachable through the published port
for df in sorted(glob.glob("A*/Dockerfile")):
    ok = "HOST=0.0.0.0" in open(df).read()
    print(("ok   " if ok else "FAIL ") + f"{df}: ENV HOST=0.0.0.0")
    if not ok:
        fails.append(df)

for f in sorted(glob.glob("A*/*/*.py")):
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        print("FAIL compile", f, e)
        fails.append(f)
print("\nFAILS:", fails if fails else "none")
sys.exit(1 if fails else 0)
