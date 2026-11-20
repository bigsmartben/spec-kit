# How to evolve specifications in an existing project

Use this guide when requirements change or implementation discoveries call for
a revision to an existing feature. It covers making the next intended contract
explicit and delivering against it, not choosing which artifacts to retain
afterward.

If the repository has not been initialized with Spec Kit yet, start with
[Adopting Spec Kit in an Existing Project](existing-projects.md).

## Assess the Change

Identify the affected behavior and review the available feature artifacts,
implementation, tests, and maintained design or product documentation.
Distinguish a defect against agreed intent from a proposed change to that intent.
The implementation is evidence for the discussion, not a replacement source of
requirements.

Decide whether the discovery changes intended behavior, a technical choice, the
task package, or only code. A discovery may originate in the frozen contract, a
work package, or the implementation, including during delivery. Its origin does
not determine which artifact is authoritative.

## Make the Revised Intent Explicit

Start from a clean working tree or a dedicated branch so every artifact change
is reviewable. Follow the team's chosen persistence convention when deciding
whether to create a new feature directory or revise retained artifacts.
If previous feature artifacts were retired, use the maintained requirements and
decision records to establish context rather than assuming the constitution
alone specifies the feature.

1. Use `/speckit.specify` to create a new feature directory under `specs/`, or
   revise the frozen `spec.md`, `prototype.html`, and `quickstart.md` together.
2. Run `/speckit.tasks` to regenerate the independently deliverable
   requirement-level work packages from that contract.
3. Run `/speckit.analyze` to report cross-artifact inconsistencies before
   implementation.

Core has no dedicated command that automatically reconciles differences among
`spec.md`, `prototype.html`, `quickstart.md`, and `tasks.md`. Analyze reports
inconsistencies without editing artifacts. Reconcile the owning stage directly,
or use an extension according to its documented behavior. Historical or
user-owned `plan.md` files can be preserved as technical records, but the core
Task stage does not read or update them.

If the team accepts a discovery that changes intent, reflect that agreement in
the affected artifacts. Do not leave a lower-level change in tasks or code
contradicting a spec that is meant to remain trustworthy.

## Deliver and Assess the Change

All persistence models use the same delivery process:
specify -> tasks -> implement.

1. Run `/speckit.implement` against the explicit intended artifacts.
2. Execute the mapped UAT scenarios and review the resulting implementation.
3. Confirm Implement changed only `Status`, `Actual Result`, `Evidence`, and
   `Deviation` in each completed `quickstart.md` UAT entry.

If execution reveals a requirement conflict or missing mapping, return to
Specify, correct the frozen contract, regenerate Task packages, and then resume
implementation. Analyze and Implement do not select a persistence strategy,
and extension-provided reconciliation does not change these core command
responsibilities.

Revising artifacts does not by itself deliver changed behavior. When a revision
requires implementation, complete this delivery loop. After delivery, apply the
team's retention and maintenance policy separately.

## See also

- [Persisting specifications](persisting-specs.md) - Choose what survives
  delivery and how retained artifacts are maintained.
- [Upgrade Spec Kit](../upgrade.md) - Refresh managed project files rather than
  changing feature requirements.
