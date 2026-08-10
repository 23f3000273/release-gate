# CI/CD Container Release Gate

Deterministic policy endpoint for GitHub Actions container releases.

## Endpoint

POST `/release-gate`

The endpoint evaluates:

- Least-privilege permissions
- Pull request trigger safety
- Test and matrix completion
- GitHub Actions pinning
- Multi-stage container builds
- Non-root execution
- Build secret safety
- Critical vulnerabilities
- Image digest pinning
- Production branch protection
- Production environment approval

## GitHub Actions

Workflow:

**TDS GA7 Release Gate**

The workflow runs on pushes to `main` and pull requests.
