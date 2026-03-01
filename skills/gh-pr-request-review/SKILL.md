---
name: dx:gh-pr-request-review
description: Request review on a GitHub PR from teams or users
user-invocable: true
invocation-name: dx:gh-pr-request-review
---

Request reviews on GitHub pull requests from teams or individual users.

## Usage

### Request review from a team

```bash
gh pr edit PR_NUMBER --add-reviewer your-org/your-team
```

### Request review from a user

```bash
gh pr edit PR_NUMBER --add-reviewer username
```

### Request review from multiple reviewers

```bash
gh pr edit PR_NUMBER \
  --add-reviewer user1 \
  --add-reviewer your-org/your-team
```

### With verification

```bash
gh pr view PR_NUMBER --json reviewRequests \
  --jq '.reviewRequests[].login // .reviewRequests[].name'
```

## Notes

- Use `--add-reviewer` with `gh pr edit` for both users and teams
- Team format: `org-name/team-slug`
- Verify the review request was assigned by checking `reviewRequests`
