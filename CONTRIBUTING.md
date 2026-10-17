# Contributing

Thanks for helping improve OpenRoute.

1. Open an issue describing the behavior and how to reproduce it.
2. Keep changes small and include tests when practical.
3. Explain any new permission, network destination, or dependency.
4. Do not add telemetry without explicit opt-in and a clear privacy explanation.
5. Do not add credential collection, stealth, persistence, or undocumented traffic routing.
6. Do not develop features intended to evade age checks, identity verification, or account-level restrictions.

Run tests with:

```bash
python -m pip install -r windows/requirements.txt
python -m pytest
```
