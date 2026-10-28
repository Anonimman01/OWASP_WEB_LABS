# Contributing

Thanks for helping improve these labs! This project is educational, so clarity matters more than cleverness.

## Ways to contribute

- Fix typos or unclear explanations in a lab `README` or `SOLUTION`.
- Improve or add translations (English is the source of truth; Russian and Uzbek follow it).
- Report a lab that does not start, or a `fixed` version that is still exploitable.
- Propose a new lab or a new defect inside an existing lab (open an issue first).

## Ground rules

1. **Keep the pair consistent.** Every defect in `vulnerable/app.py` is marked `# DEFECT N` and has a matching `# FIX N` in `fixed/app.py`. The number must match the `SOLUTION` entry.
2. **Fictional data only.** No real credentials, keys, card numbers or personal data.
3. **Local only.** Ports stay bound to `127.0.0.1` in `docker-compose.yml`.
4. **No weaponized exploits.** Show the flaw on a safe example (no RCE chains, no ready-made attack tooling).
5. **Docs in three languages.** If you change `README.md` or `SOLUTION.md`, update the `.ru` / `.uz` versions too, or say in the PR which ones still need translation.
6. **Code comments in English.** Existing Russian comments (`# ДЕФЕКТ N`) are being migrated; new code should use `# DEFECT N`.

## Before opening a pull request

```
cd AXX-lab-name
docker compose up --build
```

Check that:

- the attack from `SOLUTION` works on the `vulnerable` port;
- the same attack fails on the `fixed` port, and normal usage still works;
- the CI workflow (`labs-smoke-test`) is green.

## Pull request checklist

- [ ] Both versions start and respond
- [ ] Defect/fix numbers match the `SOLUTION`
- [ ] Docs updated (or translation gap noted)
- [ ] No real secrets or personal data
