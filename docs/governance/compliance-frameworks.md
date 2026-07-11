# Compliance Frameworks

Configured in `.sdlc/governance/compliance-policy.yaml`. `sub-compliance-validator` is dispatched in three phases:

| Phase | Focus |
|-------|-------|
| 5 — Design | Data model compliance (PII fields, retention defaults) |
| 8 — Security | Security control compliance (encryption, access controls, audit logging) |
| 12 — Retirement | Data retention/deletion compliance during decommissioning |

## Supported Frameworks

```yaml
compliance_frameworks:
  gdpr:
    enabled: true
    checks: [data_minimization, right_to_erasure, data_portability, consent_management]
  hipaa:
    enabled: false
    checks: [phi_encryption, access_controls, audit_logging]
  sox:
    enabled: false
    checks: [change_management, audit_trail]
  pci_dss:
    enabled: false
    checks: [cardholder_data_encryption, network_segmentation]
```

Enable only the frameworks relevant to your project — disabled frameworks are skipped explicitly (marked "not applicable") rather than silently ignored, so audit trails remain complete.

## Artifacts

`sub-compliance-validator` produces, under `.sdlc/artifacts/compliance/`:

- `gdpr-assessment.md` (if GDPR enabled)
- `data-flow-diagram.md`
- `privacy-impact-assessment.md`
- `compliance-sign-off.md` — final PASS/BLOCKED verdict per framework

## Blocking Behavior

A violation of an **enabled** framework blocks the relevant quality gate (Gate 5, 8, or 12) until it is either fixed or explicitly risk-accepted by a human via a CRITICAL-risk approval recorded in `decision-log.json`.
