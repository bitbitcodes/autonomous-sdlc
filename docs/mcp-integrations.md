# MCP Integrations

How to use MCP (Model Context Protocol) servers with the Autonomous SDLC Framework to auto-fetch specs from JIRA, GitHub, and other tools.

## What Is MCP?

MCP is an open protocol that lets AI IDEs connect to external services. When you configure an MCP server, the AI gains access to **tools** (functions it can call) that interact with external APIs — JIRA, GitHub, databases, etc.

The framework doesn't implement MCP itself. MCP servers run at the **IDE level**. The orchestrator is designed to **detect and use** any MCP tools that are available.

```mermaid
flowchart LR
    subgraph "Your AI IDE"
        ORCH["sdlc.orchestrator"]
        MCP_J["JIRA MCP Server"]
        MCP_G["GitHub MCP Server"]
        MCP_D["Database MCP Server"]
    end

    ORCH -->|"jira_get_issue(PROJ-123)"| MCP_J
    MCP_J -->|"Epic + Stories"| ORCH

    ORCH -->|"github_get_issue(42)"| MCP_G
    MCP_G -->|"Issue Details"| ORCH

    ORCH -->|"query(SHOW TABLES)"| MCP_D
    MCP_D -->|"Schema Info"| ORCH

    MCP_J ---|"HTTPS"| JIRA["Atlassian Cloud"]
    MCP_G ---|"HTTPS"| GH["GitHub API"]
    MCP_D ---|"TCP"| DB["PostgreSQL"]

    style ORCH fill:#6c5ce7,color:#fff,font-weight:bold
    style JIRA fill:#0052CC,color:#fff
    style GH fill:#24292e,color:#fff
    style DB fill:#336791,color:#fff
```

## How the Orchestrator Uses MCP

During **Phase 0 (Bootstrap)**, the orchestrator checks for available MCP tools in this priority order:

```mermaid
flowchart TD
    START["Spec Intake (Bootstrap)"] --> CHECK1{"User pasted spec<br/>in chat?"}
    CHECK1 -->|Yes| USE1["Use pasted spec"]
    CHECK1 -->|No| CHECK2{"Spec in<br/>.sdlc/specs/?"}
    CHECK2 -->|Yes| USE2["Use existing spec"]
    CHECK2 -->|No| CHECK3{"MCP tools<br/>available?"}
    CHECK3 -->|"JIRA MCP"| FETCH_J["Fetch epic/stories<br/>via jira_get_issue"]
    CHECK3 -->|"GitHub MCP"| FETCH_G["Fetch issue<br/>via github_get_issue"]
    CHECK3 -->|No| CHECK4{"Spec files in<br/>project root?"}
    CHECK4 -->|Yes| USE4["Use file"]
    CHECK4 -->|No| ASK["Ask user for spec"]

    USE1 & USE2 & FETCH_J & FETCH_G & USE4 & ASK --> NORM["Normalize → .sdlc/specs/normalized-spec.md"]
    NORM --> PHASE1["Begin Phase 0: Problem Discovery"]

    style START fill:#6c5ce7,color:#fff
    style PHASE1 fill:#00b894,color:#fff
```

MCP tools are also useful in later phases:
- **Phase 3 (Architecture)** — Database MCP to inspect existing schemas
- **Phase 9 (DevOps)** — GitHub MCP to create repos, configure CI
- **Phase 10 (Observability)** — Monitoring MCP servers if available

---

## JIRA MCP Server

The most impactful MCP integration. Lets the orchestrator pull epics, stories, acceptance criteria, and priorities directly from JIRA.

### Available MCP Servers

| Server | Source | Install |
|--------|--------|---------|
| **Atlassian MCP** (official) | [atlassian/mcp-server-atlassian](https://github.com/anthropics/mcp-servers) | `npx @anthropic/mcp-server-atlassian` |
| **JIRA MCP** (community) | [smithery-ai/jira-mcp](https://github.com/smithery-ai/jira-mcp) | `npx jira-mcp-server` |

### Setup

#### 1. Get Your JIRA API Token

1. Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Create an API token
3. Note your email and Atlassian domain (e.g., `company.atlassian.net`)

#### 2. Configure in Your IDE

**Devin Desktop** (formerly Windsurf) — Add to `~/.codeium/windsurf/mcp_config.json` (legacy path, still read):

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-atlassian"],
      "env": {
        "ATLASSIAN_SITE": "company.atlassian.net",
        "ATLASSIAN_USER_EMAIL": "you@company.com",
        "ATLASSIAN_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

**VS Code / Copilot** — Add to `.vscode/mcp.json` or user settings:

```json
{
  "servers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-atlassian"],
      "env": {
        "ATLASSIAN_SITE": "company.atlassian.net",
        "ATLASSIAN_USER_EMAIL": "you@company.com",
        "ATLASSIAN_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

**Claude Code** — Run:

```bash
claude mcp add atlassian \
  --env ATLASSIAN_SITE=company.atlassian.net \
  --env ATLASSIAN_USER_EMAIL=you@company.com \
  --env ATLASSIAN_API_TOKEN=your-api-token \
  -- npx -y @anthropic/mcp-server-atlassian
```

**Cursor** — Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-atlassian"],
      "env": {
        "ATLASSIAN_SITE": "company.atlassian.net",
        "ATLASSIAN_USER_EMAIL": "you@company.com",
        "ATLASSIAN_API_TOKEN": "your-api-token"
      }
    }
  }
}
```

#### 3. Use with the Framework

Once configured, select `sdlc.orchestrator` and tell it your JIRA issue:

```
Build the feature described in JIRA epic PROJ-100
```

The orchestrator will:
1. Detect the JIRA MCP tools are available
2. Call `jira_get_issue("PROJ-100")` to fetch the epic
3. Call `jira_search("parent = PROJ-100")` to fetch all child stories
4. Extract titles, descriptions, acceptance criteria, priorities
5. Normalize everything into `.sdlc/specs/normalized-spec.md`
6. Begin Phase 0: Problem Discovery

```mermaid
sequenceDiagram
    participant You
    participant Orch as Orchestrator
    participant MCP as JIRA MCP Server
    participant JIRA as Atlassian Cloud

    You->>Orch: "Build PROJ-100"
    Orch->>MCP: jira_get_issue("PROJ-100")
    MCP->>JIRA: GET /rest/api/3/issue/PROJ-100
    JIRA-->>MCP: Epic details
    MCP-->>Orch: {summary, description, ...}

    Orch->>MCP: jira_search("parent = PROJ-100")
    MCP->>JIRA: GET /rest/api/3/search?jql=...
    JIRA-->>MCP: 5 child stories
    MCP-->>Orch: [{story1}, {story2}, ...]

    Orch->>Orch: Normalize → .sdlc/specs/normalized-spec.md
    Orch->>Orch: Begin Phase 1
```

### What Gets Fetched

| JIRA Field | Used For |
|------------|----------|
| Summary | Requirement title |
| Description | Requirement details |
| Acceptance Criteria (custom field) | Test generation in Phase 5 |
| Priority | Task ordering in Phase 3 |
| Labels | Tech stack detection |
| Story Points | Complexity estimation |
| Components | Architecture decisions |
| Fix Version | Constraint/deadline |
| Sub-tasks | Task breakdown hints |

---

## GitHub MCP Server

Useful for fetching GitHub Issues as specs and for DevOps phase integration.

### Setup

**Devin Desktop / Cursor / VS Code** — Add to your MCP config:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

**Claude Code:**

```bash
claude mcp add github \
  --env GITHUB_TOKEN=ghp_your_token_here \
  -- npx -y @anthropic/mcp-server-github
```

### Usage

```
Build the feature described in GitHub issue #42
```

The orchestrator fetches the issue body, labels, and linked issues as the spec.

### Useful in Later Phases

| Phase | GitHub MCP Use |
|-------|---------------|
| Phase 0 | Fetch issues as specs |
| Phase 5 | Create branches, check existing code |
| Phase 8 | Create pull requests |
| Phase 9 | Configure GitHub Actions CI/CD |

---

## Database MCP Server

Useful in **Phase 3 (Architecture)** to inspect existing database schemas.

### Setup

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/mydb"
      }
    }
  }
}
```

### Usage

The orchestrator can use database MCP tools during Phase 3 to:
- Inspect existing table schemas
- Understand current data model before designing extensions
- Check for naming conventions and patterns
- Avoid proposing migrations that conflict with existing structure

---

## Other Useful MCP Servers

| MCP Server | Use Case | Phase |
|------------|----------|-------|
| **Linear** | Fetch Linear issues as specs | Phase 0 |
| **Notion** | Fetch Notion pages as PRDs | Phase 0 |
| **Slack** | Post status updates to channels | All |
| **Sentry** | Fetch error reports for bug specs | Phase 0 |
| **Filesystem** | Extended file operations | Phase 4 |
| **Memory** | Persistent key-value memory | All |

MCP servers are added the same way — configure in your IDE's MCP config, and the orchestrator will use available tools when relevant.

---

## Security Notes

- **Never commit API tokens** — Use environment variables or IDE-level config files (which are outside your repo)
- **Scope tokens minimally** — JIRA: read-only is sufficient for spec fetching. GitHub: `repo` scope for full integration
- **MCP configs are IDE-local** — `.vscode/mcp.json` and `~/.codeium/windsurf/mcp_config.json` (Devin Desktop's legacy path) are typically gitignored or outside the repo
- If you must share MCP config in a team, use placeholder values and document the required env vars

## Troubleshooting

### "The orchestrator didn't use MCP"

- Verify the MCP server is running: check your IDE's MCP status panel
- Confirm the tool names match what the orchestrator expects (it looks for tools containing `jira`, `github`, `issue`, etc.)
- Try explicitly saying: "Use the JIRA MCP to fetch PROJ-123"

### "MCP server fails to connect"

- Check your API token is valid and not expired
- Verify the Atlassian domain / GitHub org is correct
- Check network connectivity (VPN may be required for corporate JIRA)
- Look at the IDE's MCP server logs for specific errors

### "Fetched spec is incomplete"

- JIRA's Atlassian Document Format (ADF) can be complex — some formatting may be lost
- Check that acceptance criteria are in a standard custom field
- You can supplement MCP-fetched data by adding extra context in your chat message
