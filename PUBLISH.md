# Publish

This package is published as:

- package name: `oomol-fusion-sdk`
- import path: `oomol_fusion_sdk`
- version: `2.0.0`

## Preflight

Regenerate raw OpenAPI types if needed:

```bash
python3 scripts/generate_openapi_types.py
```

Or point to the shared snapshot explicitly:

```bash
python3 scripts/generate_openapi_types.py --spec ../oomol-fusion-sdk-ts/openapi.full.snapshot.json
```

Run tests:

```bash
python3 -m unittest discover -s tests
```

## Build

Build source and wheel distributions:

```bash
python3 -m build
```

Optional check:

```bash
twine check dist/*
```

## Upload

Upload to PyPI:

```bash
twine upload dist/*
```

Use PyPI token authentication:

- username: `__token__`
- password: `<pypi-token>`

## Notes

- The Python SDK version should stay aligned with `oomol-fusion-sdk-ts`
- Raw OpenAPI types are generated into `src/oomol_fusion_sdk/generated/openapi_types.py`
- Public convenience aliases live under `oomol_fusion_sdk.aliases`
