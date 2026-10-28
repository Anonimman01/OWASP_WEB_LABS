# Security Policy

## Intentionally vulnerable code

The applications in the `vulnerable/` folders of this repository are **deliberately insecure** and exist for training. Reports about vulnerabilities in these folders (SQL injection, weak crypto, default passwords, outdated dependencies in lab A03, etc.) are **not security issues**. They are the point of the labs.

Please do not open security reports for them, and never expose these apps to the internet.

## What counts as a real issue

Please report privately if you find:

- a flaw in a `fixed/` version that is **not** documented in that lab's `SOLUTION` (the fix is incomplete or bypassable);
- a lab that can be reached from outside `127.0.0.1` with the provided `docker-compose.yml`;
- real secrets, tokens or personal data committed to the repository;
- a problem in the CI workflow or Dockerfiles that could affect people running them.

## How to report

Use GitHub's **"Report a vulnerability"** button on the Security tab of this repository (private advisory). If that is unavailable, open an issue with the title "Security contact request" and no technical details, and I will reach out.

I aim to respond within 7 days.
