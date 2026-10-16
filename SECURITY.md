# Security

- The review prompt treats PR text and requests as data, not instructions.
- GitHub Actions makes no model calls and runs with read-only permissions; pinned action SHAs.
- The merge guard checks consistency of captured data, not its origin. On plans
  without branch protection, the merge button and direct pushes bypass it.

Report vulnerabilities privately to the repository owner via GitHub security advisories.
