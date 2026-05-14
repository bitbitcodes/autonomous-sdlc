# Structured Prompting

Every agent dispatch — whether from orchestrator to stage agent or from stage agent to subagent — must use the structured prompt format. This ensures consistent, high-quality outputs.

---

## The Four Sections

Every dispatch prompt MUST include these four sections:

### 1. GOAL
What success looks like — measurable outcome.

**Good (API project):**
> Create POST /api/users endpoint. Success: endpoint returns 201, tests pass, matches interface contract.

**Good (CLI project):**
> Implement `config set` command. Success: command writes config to ~/.myapp/config.yaml, exit code 0, help text matches CLI spec.

**Bad:**
> Implement user registration functionality.

### 2. CONSTRAINTS
Hard limits — what you cannot do.

**Good:**
> - Use bcrypt for password hashing (already in dependencies)
> - No new dependencies without approval
> - Response time < 200ms

**Bad:**
> - Write good code
> - Follow best practices

### 3. CONTEXT
Files to read, previous attempts, related decisions.

**Good:**
> - Existing auth pattern: src/auth/login.ts
> - Interface contract: .sdlc/artifacts/design/interface-contracts.* (relevant section)
> - User model: src/models/user.ts
> - Previous attempt failed with: "bcrypt not imported" (see learnings)

**Bad:**
> - Check the codebase for context

### 4. OUTPUT
Exact deliverables expected — file paths, formats, checklists.

**Good:**
> - [ ] Endpoint implementation in src/routes/users.ts
> - [ ] Unit tests in tests/users.test.ts (≥ 3 tests: happy path, duplicate email, invalid input)
> - [ ] Integration test in tests/integration/users.test.ts

**Bad:**
> - Working code with tests

---

## Full Example

```
## GOAL
Create POST /api/users endpoint that registers new users.
Success: Endpoint works, returns 201 with user object, tests pass, matches interface contract.

## CONSTRAINTS
- Use bcrypt for password hashing (already in dependencies)
- No new dependencies without approval
- Response time < 200ms
- Email must be unique (409 on duplicate)
- Password must be ≥ 8 characters

## CONTEXT
- Existing auth pattern: src/auth/login.ts
- Interface contract: .sdlc/artifacts/design/interface-contracts.yaml (POST /api/users)
- User model: src/models/user.ts
- Database: PostgreSQL, using Prisma ORM
- Validation: Zod (see src/validation/schemas.ts for pattern)

## OUTPUT
- [ ] Endpoint: src/routes/users.ts
- [ ] Validation schema: src/validation/user.schema.ts
- [ ] Unit tests: tests/routes/users.test.ts (happy path + 3 error cases)
- [ ] Integration test: tests/integration/users.test.ts
```

---

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Fix |
|-------------|-------------|-----|
| Vague GOAL | Agent doesn't know when it's done | Add measurable success criteria |
| No CONSTRAINTS | Agent may make harmful decisions | List hard limits explicitly |
| Empty CONTEXT | Agent wastes time exploring | Point to exact files and sections |
| Vague OUTPUT | Agent produces wrong format | Specify file paths and checklists |
| Too many GOALs | Agent loses focus | One GOAL per dispatch |
| Contradictory CONSTRAINTS | Agent is stuck | Review constraints for conflicts |

---

## Prompt Size Guidelines

| Agent Type | Ideal Prompt Size | Max |
|-----------|------------------|-----|
| Subagent (focused task) | 200-500 tokens | 1000 |
| Stage agent | 500-1500 tokens | 3000 |
| Orchestrator | 1000-3000 tokens | 5000 |

Keep prompts focused. More context ≠ better output. Include only what the agent needs for its specific task.
