# How to adopt Spec Kit in an existing project

You do not need to recreate an existing system from specifications before using
Spec Kit. Initialize the repository in place, capture the rules that matter,
and use the workflow for the next bounded change.

## 1. Start from a Reviewable Baseline

Before initialization, commit or stash existing work and create a branch for the
adoption. This makes every generated file visible in a normal code review.

Choose the [integration key](../integrations/index.md) for the coding agent
you use. Then run the command from the repository root:

```bash
specify init --here --force --integration <key>
```

`--here` targets the current directory. `--force` allows initialization in a
non-empty directory and may replace files at conflicting managed paths, so use
it only after creating a reviewable baseline. It does not delete the rest of
your application.

Review the resulting diff before continuing. Initialization adds the shared
`.specify/` project files and the command or skill files required by your
selected integration. It does not rewrite your application or infer
specifications for existing behavior.

> [!NOTE]
> Git initialization and feature branches are optional and are managed by the
> **git** extension. Add it with `specify extension add git` if you want that
> workflow.

## 2. Capture Project Guardrails

The remaining steps illustrate adopting **SDD** for a bounded feature. If your
first task is a repair, you can instead follow the
[bug-fixing quickstart](../guides/bugfix.md) after initialization; to evaluate a proposal,
use the [idea assessment quickstart](../guides/assessment.md). Neither process requires
completing the SDD steps below first.

The examples below use GitHub Copilot's default skills mode (`/speckit-*`).
Invoke each skill separately in your agent's chat, not in the terminal, and
review the result before moving to the next step.

Run `/speckit-constitution` with principles that are already true for the
repository or that the team has explicitly agreed to adopt:

```text
/speckit-constitution Preserve public API compatibility. Follow the existing
service boundaries. Every database migration must include a rollback plan.
Run the repository's established unit and integration test suites.
```

Use the repository's README, architecture decisions, contribution guide, and
CI configuration as evidence. Do not invent standards merely to fill the
constitution template. The constitution governs later task packaging and
implementation, so unrealistic rules create noise instead of useful
constraints.

## 3. Choose a Bounded First Change

Start with a feature or modernization slice that can be reviewed
independently. Do not make "document the entire existing system" your first
feature unless that inventory is itself the intended deliverable.

Describe both the requested outcome and the compatibility boundaries that must
remain intact:

```text
/speckit-specify Add CSV export to the existing orders page. Preserve current
filters and authorization behavior. Export only the rows visible to the signed-in
user, and do not change the existing JSON API response.
```

The codebase remains implementation context. The new `spec.md` defines the
change you intend to make, not a retroactive specification of every existing
behavior.

## 4. Package and Implement the Change

Continue through the normal workflow:

1. Run `/speckit-clarify` to resolve uncertain behavior and compatibility
   requirements.
2. Run `/speckit-tasks`. Task reads only the frozen `spec.md`,
   `prototype.html`, `quickstart.md`, and the constitution, so package the
   change without relying on inferred technical facts from the repository.
3. Run `/speckit-analyze` to check contract and work-package consistency.
4. Run `/speckit-implement`. Implement may inspect the codebase and owns the
   decisions about stack reuse, architecture, files, and paths.
5. Review code and UAT-result changes together. Implement records only
   `Status`, `Actual Result`, `Evidence`, and `Deviation` in the matching
   `quickstart.md` UAT entries.

Existing code is implementation context, not a reason for Task to lock a
technical approach. If the work exposes a requirement conflict or missing
acceptance rule, return it to Specify or Clarify rather than resolving the
product question in code.

For command details and optional quality gates, see the
[Quick Start Guide](../quickstart.md) and
[Agentic SDD reference](../reference/agentic-sdd.md).

## 5. Decide How Specs Will Age

After the first change, agree on what feature artifacts the team will retain
and how retained artifacts will be maintained. The
[Persisting Specifications](persisting-specs.md) page compares those choices, including
retiring completed feature artifacts under the constitution-only model. Use the
[Evolving Specs guide](evolving-specs.md) when delivering a subsequent change.

## Existing-Project Examples

The [community walkthroughs](../community/walkthroughs.md) include brownfield
examples across .NET, Java, and Go/React codebases. Community extensions for
architecture discovery and brownfield bootstrapping are listed in the
[extension catalog](../community/extensions.md).

## See also

- [Command invocation](../integrations/cli.md#command-invocation) — syntax
  for other coding agents and integration modes.
