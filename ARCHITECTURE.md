# Architecture (MVP)

## Windows

`windows/app.py` is a small GUI and diagnostic runner. `check_host` performs DNS resolution followed by an HTTPS request. It does not write system configuration, intercept packets, route traffic, or collect telemetry.

## Android

The Android directory is currently documentation-only. A future client should perform transparent foreground tests first. Do not add VPN routing without explicit user consent, a documented threat model, leak-handling behavior, and security review.

## Failure interpretation

A DNS failure or HTTPS failure does not by itself prove censorship. Possible explanations include a local configuration issue, captive portal, DNS resolver failure, transient outage, firewall, TLS interception, or network filtering.
