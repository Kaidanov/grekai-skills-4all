# Contributing to GrekAI Skills 4 All

Thanks for being here — **PRs are welcome** 🙌. This is an open, free catalog of agent skills.
Use anything here under the [MIT License](./LICENSE); contributions of your own skills, fixes, and
improvements are encouraged.

## Ways to contribute

- **Improve an existing skill** — clearer docs, bug fixes, more examples.
- **Add a new skill** — see [`skills/README.md`](./skills/README.md): copy `skills/_template/`,
  write a `SKILL.md` + `README.md`, and register it in [`skills.json`](./skills.json) and the root
  README catalog table.
- **File an issue** — ideas, bugs, or requests.

## Ground rules

- **No secrets.** Never commit credentials, tokens, private profiles, or customer data — redact to
  `${env:NAME}` placeholders. Keep skills generic and reusable.
- **Self-contained.** A skill lives in its own folder and shouldn't depend on this repo's internals.
- **Be kind.** Assume good faith; keep discussion respectful and on-topic.

## Submitting a PR

1. Fork + branch (`feat/<thing>` or `fix/<thing>`).
2. Keep changes focused; update the relevant README(s).
3. Open the PR against `main` with a short description of what and why.
4. Maintainer review → merge → the site auto-deploys.

## Credits & contact

Created and maintained by **Tzvi Gregory Kaidanov** — **[Set4u](https://set4u.biz)**.
Reach out via [set4u.biz](https://set4u.biz). If this catalog helps you, a ⭐ on the repo is
hugely appreciated and helps others find it.
