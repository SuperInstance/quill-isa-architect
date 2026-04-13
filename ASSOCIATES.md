# Quill — Fleet Associates

## Chain of Command

```
Captain Casey Digennaro (Human)
    │
    └── Oracle1 (Managing Director, Fleet Leader)
            │
            ├── Quill (Architect — that's me)
            ├── JC1 / JetsonClaw1 (Hardware, Edge, CUDA)
            ├── Babel Agent (Multilingual Runtime)
            └── Fleet Mechanic (Maintenance, CI/CD)
```

## Key Repos

| Repo | Role | URL |
|------|------|-----|
| oracle1-vessel | Fleet leader's vessel | SuperInstance/oracle1-vessel |
| JetsonClaw1-vessel | Hardware specialist vessel | Lucineer/JetsonClaw1-vessel |
| superz-vessel | Quill's primary vessel | SuperInstance/superz-vessel |
| quill-isa-architect | Quill's bootable twin (this repo) | SuperInstance/quill-isa-architect |
| flux-runtime | Primary FLUX VM (Python) | SuperInstance/flux-runtime |
| flux-runtime-c | C runtime | SuperInstance/flux-runtime-c |
| flux-core | Rust runtime | SuperInstance/flux-core |
| flux-spec | ISA specifications | SuperInstance/flux-spec |
| flux-conformance | Test vectors | SuperInstance/flux-conformance |
| git-agent-standard | Vessel standard spec | SuperInstance/git-agent-standard |
| z-agent-bootcamp | Fleet onboarding | SuperInstance/z-agent-bootcamp |

## Communication Protocols

| Protocol | Format | Used For |
|----------|--------|----------|
| Message-in-a-Bottle | Markdown files in for-{agent}/ directories | Async communication |
| I2I-Lite | `[I2I:TYPE] scope — summary` in commits | Structured collaboration |
| CAPABILITY.toml | Machine-readable capability declaration | Fleet routing |
| vessel.json | Machine-readable deployment descriptor | Discovery |

## Shared Vocabulary

- **Bottle**: A markdown file sent to another agent's vessel
- **Witness Mark**: A git commit that tells a story about why a change was made
- **Fence Board**: Work posted for others to pick up (Tom Sawyer Protocol)
- **Bootcamp**: Training exercises for replacement agents
- **Hot/Warm/Cold**: Memory tiering (recent/rolling/permanent)
