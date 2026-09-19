# Contributing

Open an issue before adding a new desktop version. A version profile needs exact source hashes, one-to-one transformations, semantic tests, route checks and two fresh isolated launches. Do not submit official package files, extracted bundles, real sessions, databases, credentials or personal paths.


## Exact 26.915.4065.0 bundle regressions

The portable bundle is not distributed in this repository. After building it locally, opt into the 12 real-bundle checks in addition to the ordinary public test suite:

```powershell
$env:CODEX_WORKFLOW_TEST_ASAR = "C:/codex-workflow/app/resources/app.asar"
python -m unittest discover -s tests -v
```

Without this environment variable, that test class is explicitly skipped. An explicitly provided missing or incompatible artifact fails; it is not silently skipped. The public CI runner does not obtain official binaries.
