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
~/.claude/tools/gh-request-review.py \
  --pr PR_NUMBER \
  --reviewer org-name/team-slug
```

### Request review from a user

```bash
~/.claude/tools/gh-request-review.py \
  --pr PR_NUMBER \
  --reviewer username
```

### Request review from multiple reviewers

```bash
~/.claude/tools/gh-request-review.py \
  --pr PR_NUMBER \
  --reviewer user1 \
  --reviewer user2 \
  --reviewer org-name/team-slug
```

### With verification

```bash
gh pr view PR_NUMBER --json reviewRequests \
  --jq '.reviewRequests[].login // .reviewRequests[].name'
```

## Notes

- Use `gh-request-review.py` for requesting reviews (handles both users and teams)
- Team format: `org-name/team-slug`
- Verify the review request was assigned by checking `reviewRequests`
