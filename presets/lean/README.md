# Lean Workflow

A minimal preset that strips the Spec Kit workflow down to its essentials — just the prompt, just the artifact.

## When to Use

Use Lean when you want the structured Specify → Task → Implement pipeline without the ceremony of the full templates. Specify freezes the product contract, Task converts it into requirement-level work packages, and Implement owns the technical execution.

## Commands Included

| Command | Output | Description |
|---------|--------|-------------|
| `speckit.specify` | `spec.md`, `prototype.html`, `quickstart.md` | Create a specification, construction-contract prototype, and pending UAT baseline |
| `speckit.tasks` | `tasks.md` | Create traceable requirement-level work packages without technical or file-path lock-in |
| `speckit.implement` | *(code)*, `tasks.md`, `quickstart.md` | Choose the implementation and execute tasks plus UAT |
| `speckit.constitution` | `constitution.md` | Create or update the project constitution |

## What It Replaces

Lean overrides the four active core workflow commands with self-contained prompts that consume and produce the artifacts directly — no separate template files involved. The result is a shorter, more direct workflow.

## Installation

```bash
# Lean is a bundled preset — no download needed
specify preset add lean
```

## Development

```bash
# Test from local directory
specify preset add --dev ./presets/lean

# Verify commands resolve
specify preset resolve speckit.specify

# Remove when done
specify preset remove lean
```

## License

MIT
