# Contributing

Solo-maintained, but run like a team repo: every change goes through the same checks.

## Dev setup

```bash
make setup     # frontend deps + local tooling notes
make check     # everything CI runs: consistency, lint, terraform, frontend, backend smoke
```

Individual pieces: `make lint` (ruff + prettier), `make test` (backend smoke), `make fmt`
(auto-format), `make corpus-dry` (chunker stats without AWS). See the [Makefile](Makefile).

## Ground rules

- **Content edits** (guides, cram, exams) follow the contract in [CLAUDE.md](CLAUDE.md):
  answer-key corrections leave `> Note:` blocks, fast-moving facts get `*(point-in-time)*` flags
  plus a [VERIFICATION-LOG.md](VERIFICATION-LOG.md) row, and never assert an AWS capability
  boundary without checking current docs.
- **Code** must pass `make check` before pushing. CI enforces the same suite; `main` is
  branch-protected on it.
- **Factual claims about AWS** in any new content need a source. Found an error instead? Open a
  [content-error issue](.github/ISSUE_TEMPLATE/content-error.yml) with the doc link.
- Infrastructure changes: `terraform plan` output belongs in the PR description; applies are
  human + local, never CI (see [website/CICD-SPEC.md](website/CICD-SPEC.md)).

## PR checklist

The [PR template](.github/pull_request_template.md) asks for: what changed and why, `make check`
green, VERIFICATION-LOG rows for any new point-in-time facts, and CHANGELOG entry for anything
user-visible.
