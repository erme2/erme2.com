# erme2.com

Personal website for Arduino Di Giosia, built with Astro.

## Development

```sh
npm install
npm run dev
```

## Build

```sh
npm run build
```

## Deployment

The `Deploy` GitHub Actions workflow builds the Astro site and uploads `dist/`
to Hostinger over SSH.

Configure these repository secrets before running it:

- `HOSTINGER_HOST`: SSH hostname for the Hostinger account.
- `HOSTINGER_USERNAME`: SSH username.
- `HOSTINGER_SSH_PRIVATE_KEY`: private key with write access to the hosting account.
- `HOSTINGER_TARGET_DIR`: remote document root, usually something like `/home/USER/domains/erme2.com/public_html`.
- `HOSTINGER_PORT`: optional SSH port. Defaults to `22` when omitted.
