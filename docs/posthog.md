# PostHog Setup

erme2.com uses PostHog for lightweight website analytics and initial session
replay experiments. Keep the setup small: the site is a public Astro site, not a
product funnel with billing, CRM, or customer data sources.

## Project Settings

- Project name: `erme2.com`
- Timezone: `Europe/London`
- Data sources: none initially
- Session replay: enabled initially, with conservative privacy settings
- Autocapture: disabled or kept minimal; prefer explicit events for important
  interactions

Do not connect Stripe, HubSpot, databases, or other warehouse sources until
there is a concrete product question that requires correlation with those
systems.

## Environment Variables

Configure analytics through public build-time environment variables:

```sh
PUBLIC_POSTHOG_KEY=phc_public_project_key
PUBLIC_POSTHOG_HOST=https://eu.i.posthog.com
```

Use the PostHog project token from the browser/Web SDK install snippet. Do not
commit personal API keys, private API keys, session tokens, or project secrets.

The site must work without these variables. When `PUBLIC_POSTHOG_KEY` is absent,
analytics and replay should not initialize.

## Initial Capture Scope

The initial implementation disables broad autocapture and tracks only explicit
events from marked links.

Track:

- Page views.
- Project repository link clicks.
- Pane demo clicks.
- CV link or download clicks.
- Other important outbound GitHub links.

Avoid:

- Identifying visitors.
- Capturing form input.
- Recording unnecessary personal data.
- Sending deployment secrets or private repository data.

## Session Replay

Session replay may be enabled for the initial experiment because the site is
mostly static and has no sensitive product workflow. Keep it privacy-conscious:

- Mask all inputs.
- Mask or block sensitive elements if any are added later.
- Disable replay in PostHog settings or in code if it stops being useful.

If the site later adds forms, authentication, account pages, or private data,
revisit this decision before deploying those changes.

## Later MCP Setup

After the PostHog MCP/tool connection is available, use it to verify project
settings rather than to broaden tracking scope. The expected settings are:

- Project timezone remains `Europe/London`.
- Session replay is enabled only with input masking.
- No external data sources are connected.
- Events are limited to page views and explicit interaction events.
