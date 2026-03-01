# dev10x Claude Plugin

A Claude Code plugin that turns your CLI into a senior engineering
partner. Ships 28 skills that automate the tedious parts of your
dev workflow — structured commits, PR lifecycle, branch hygiene,
task tracking, and more — so you stay in flow.

## What you get

**Git workflow on autopilot.** Type `/commit` and get a properly
formatted commit with gitmoji, ticket reference, and JTBD
outcome-focused title — extracted from your branch name and diff.
No more context-switching to remember conventions.

**PR lifecycle from create to merge.** `/pr:create` pushes your
branch, writes a Job Story description, links the ticket, and
opens a draft PR. `/pr:monitor` watches CI and review comments
in the background, auto-fixing issues with fixup commits.
`/pr:respond` triages and addresses reviewer feedback in batch.

**Branch history that tells a story.** `/branch:groom` restructures
your commits into atomic, well-organized units before merge.
`/commit:split` breaks monolithic commits into Clean Architecture
layers. No more "fix stuff" commits surviving into main.

**Task tracking without leaving the terminal.** `/dx:tasks` tracks
in-session work items. `/dx:defer` saves items for later.
`/dx:wrap-up` captures unfinished work at session end so nothing
falls through the cracks.

**Safe git operations.** The `dx:git` skill guards against
force-pushes to protected branches and ensures rebases run safely.
Worktree support (`/dx:git-worktree`) gives you isolated
workspaces for parallel feature work.

**Issue tracker integration.** Works with GitHub Issues, Linear,
and JIRA. `/ticket:create` creates tickets. `/commit:to-new-ticket`
retroactively converts commits into tracked issues.

## Skill families

| Family | Skills | What it automates |
|--------|--------|-------------------|
| **Git** | `/commit`, `/commit:split`, `/commit:fixup`, `/branch:groom` | Structured commits, atomic history |
| **PR** | `/pr:create`, `/pr:review`, `/pr:respond`, `/pr:monitor` | Full PR lifecycle |
| **Tasks** | `/dx:tasks`, `/dx:defer`, `/dx:todo`, `/dx:wrap-up` | In-session work tracking |
| **Tickets** | `/ticket:create`, `/ticket:branch`, `/commit:to-new-ticket` | Issue tracker integration |
| **Tooling** | `/dx:git`, `/dx:git-worktree`, `/dx:py-uv` | Safe operations, workspace isolation |
| **Meta** | `/dx:skill-create`, `/dx:skill-audit` | Create and audit skills |

Run any skill by typing its name in the Claude Code CLI — e.g.,
`/commit` or `/pr:create`.

## Installation

### Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)
  installed and authenticated
- Git 2.20+ (for worktree support)
- GitHub CLI (`gh`) installed and authenticated

### 1. Clone the repo

This is a private repository. You need GitHub access granted through
the [Dev10x community](https://www.skool.com/dev10x-1892). Once you
have access:

```bash
git clone git@github.com:wooyek/dev10x-claude-plugin.git \
  ~/.claude/plugins/dev10x-claude-plugin
```

> **Using HTTPS?** Replace the URL with
> `https://github.com/wooyek/dev10x-claude-plugin.git` and
> authenticate when prompted.

### 2. Register the plugin

Tell Claude Code to load the plugin on every session:

```bash
claude plugin add --local ~/.claude/plugins/dev10x-claude-plugin
```

### 3. Verify the installation

Start a new Claude Code session and check that skills are loaded:

```bash
claude
# Inside the session, type:
/dx:skill-motd
```

You should see a skills reference listing all available commands.

### Alternative: load for a single session

If you want to try the plugin without a permanent install:

```bash
claude --plugin-dir ~/.claude/plugins/dev10x-claude-plugin
```

### Updating

Pull the latest changes to stay current:

```bash
cd ~/.claude/plugins/dev10x-claude-plugin && git pull
```

## Getting access

This plugin is available to members of the
[Dev10x community on Skool](https://www.skool.com/dev10x-1892).
To get access:

1. Join the community at https://www.skool.com/dev10x-1892
2. Share your GitHub username in the community
3. You will be added as a collaborator to the private repo
4. Clone and install using the steps above

## Development

Test locally without installing:

```bash
claude --plugin-dir /path/to/dev10x-claude-plugin
```

Validate plugin structure:

```bash
claude plugin validate /path/to/dev10x-claude-plugin
```

## License

MIT
