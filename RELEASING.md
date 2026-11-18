# Releasing

The first release can be uploaded with an account-level PyPI API token. Never commit tokens to this repository. Use a protected credential store or pass credentials through the upload process environment.

```bash
python -m pytest -q
python -m build
python -m twine check --strict dist/*
python -m twine upload --non-interactive dist/*
```

For later releases, configure a GitHub Trusted Publisher in the PyPI project settings:

- Owner: `lastexam-org`
- Repository: `lastexam`
- Workflow filename: `publish.yml`
- Environment: `pypi`

Create the `pypi` GitHub environment and apply the desired reviewer restrictions. This repository includes the workflow but does not configure the PyPI trust relationship automatically. The `Publish to PyPI` workflow runs when a GitHub release is published, tests and builds the tagged source, then uploads with OIDC. It requires the trust relationship to be configured first.

Increment `project.version` in `pyproject.toml` and `__version__` in `src/lastexam/__init__.py` before a new release. Build from a clean tree, check package contents, and tag the tested commit. PyPI release files cannot be overwritten. Verify installation from PyPI in a fresh environment after upload.
