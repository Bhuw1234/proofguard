# Qodo Code Review Evidence

This file documents the Qodo code review process for ProofGuard.

## What You Need to Capture

For the hackathon submission, you need evidence of Qodo reviewing a substantive pull request. Here's exactly what to collect:

### 1. A Real Merged Pull Request

- Create a feature branch (e.g. `feature/counterfactual-sandbox`)
- Push the core backend code (safety engine, API, tests)
- Open a pull request on GitHub
- The PR should contain substantive code changes, not just docs

### 2. Qodo Review

- Install Qodo on your GitHub repository (via GitHub Marketplace or Qodo's setup instructions)
- Qodo should automatically review the pull request when opened
- If it doesn't trigger automatically, check Qodo's documentation for manual trigger options

### 3. What to Record

After Qodo reviews your PR:

1. **Public PR URL** — Copy the full URL of the merged pull request
2. **Qodo finding** — Pick one real issue Qodo raised (e.g. "missing input validation", "potential SQL injection", "unused import", etc.)
3. **Action taken** — What did you do about it? Fix it, or explain why it's not applicable?
4. **Follow-up review** — After pushing fixes, did Qodo review again? Link to the follow-up

### 4. Fill In the README

Replace the placeholders in README.md:

```md
## Qodo Code Review Evidence

Representative merged pull request:

[PR #X — Add counterfactual SQL sandbox](https://github.com/YOUR_USERNAME/proofguard/pull/X)

Qodo surfaced:

- (paste actual Qodo finding here)

Action taken:

- (describe what you did)

Follow-up review:

[View follow-up review](https://github.com/YOUR_USERNAME/proofguard/pull/X#issuecomment-XXXXXXX)
```

## Suggested PR Workflow

1. Start on `main` with docs and skeleton files
2. Create branch: `git checkout -b feature/counterfactual-sandbox`
3. Add backend code: safety engine, API, tests
4. Push and open PR
5. Wait for Qodo review
6. Fix issues, push to same branch
7. Merge after review

This gives you a clean, honest review trail.
