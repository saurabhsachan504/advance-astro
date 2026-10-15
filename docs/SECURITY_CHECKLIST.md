# Production security checklist

- [ ] Replace every value in `.env`; keep it out of Git and rotate secrets after any disclosure.
- [ ] Terminate TLS at Caddy/Traefik and expose only ports 80/443 through Cloudflare Tunnel.
- [ ] Keep Postgres, Redis, MinIO, Qdrant and vLLM on a private Docker network with no host ports.
- [ ] Enable an authentication provider and row-level authorization before any user data is saved.
- [ ] Add signed MinIO URLs, ClamAV/malware scan, magic-byte validation, EXIF removal and image re-encoding before enabling file upload.
- [ ] Encrypt stored assets and sensitive birth data with managed/rotated keys.
- [ ] Make raw-image deletion and data export/erasure jobs tested and observable.
- [ ] Add rate limits, CSP, HSTS, CSRF/session protection, audit logs and redacted error logging.
- [ ] Pin/review container images and Python/Node dependencies; scan in CI.
- [ ] Test backup restoration and account isolation before launch.

