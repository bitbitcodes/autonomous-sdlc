# Approval Workflows

Three channels can resolve a pending approval request. All three write to the same `.sdlc/governance/pending-approvals.json` and `decision-log.json`, so any channel can be used interchangeably.

## 1. CLI

```bash
sdlc approvals list                       # Show pending approvals
sdlc approvals list --all                 # Include resolved approvals
sdlc approvals approve APPR-001           # Approve
sdlc approvals reject APPR-001 --reason "Use MySQL instead"
sdlc approvals configure                  # Set up Slack/email notifications
```

## 2. Web Dashboard

`sdlc dashboard` (existing real-time dashboard) surfaces an Approvals tab showing pending requests with full context (decision, alternatives, risk level) and Approve/Reject buttons.

## 3. IDE Chat

When an agent hits a HIGH/CRITICAL decision mid-conversation, it injects an approval request directly into the chat (see `templates/approval-prompt.md`). Reply `approve` or `reject: <reason>` to resume the agent inline — no context switch required.

## Notification Channels

Configure in `.sdlc/governance/notification-config.yaml` (or via `sdlc approvals configure`):

```yaml
channels:
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/..."
  email:
    enabled: true
    to_addresses: ["lead@example.com"]
  desktop:
    enabled: false
default_channel: "slack"
```

If no channel is enabled, requests fall back to being visible only via `sdlc approvals list` / the IDE chat.
