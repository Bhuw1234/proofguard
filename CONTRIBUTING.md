# Contributing to ProofGuard

## Workflow

1. Do not push substantive work directly to `main`.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes and commit.
4. Open a GitHub pull request against `main`.
5. Run or request Qodo review on the pull request.
6. Fix valid issues that Qodo raises.
7. Push fixes to the same pull request.
8. Ensure a follow-up review happens after fixes.
9. Merge only after review is complete.

## Code Style

- Python: follow standard PEP 8
- JavaScript/JSX: keep it simple, no complex abstractions
- CSS: use the design tokens defined in `index.css`
- Write short docstrings that explain *why*, not *what*
- Add tests for new backend functionality

## Running Tests

```bash
cd backend
source .venv/bin/activate
pytest -q
```

## Qodo Review

This project uses Qodo for automated code review on pull requests. When you open a PR:

1. Qodo will review the changes automatically (if configured on the repository)
2. Review the suggestions Qodo makes
3. Fix genuine issues or explain why a suggestion doesn't apply
4. Push follow-up commits to the same PR
5. Request a follow-up review if substantial changes were made

Evidence of Qodo reviews is tracked in [docs/qodo-evidence.md](docs/qodo-evidence.md).
