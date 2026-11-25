# Shared observatory scheduler source

This is an independent copy of the shared GitHub workflow dispatcher. The template
registry is intentionally **empty** and the example Worker has a different name.
Creating or cloning this repository does not alter the deployed scheduler.

For a new site's own repository, add a reviewed record to the existing runner's
complete current registry (or prepare a separately authorized runner):

```js
Object.freeze({
  id: 'new-token', owner: 'YOUR_OWNER', repo: 'YOUR_REPOSITORY',
  workflow: 'update.yml', ref: 'main', everyMinutes: 30,
  phaseMinutes: 0, enabled: true
})
```

The worker ticks every ten minutes. Every 30-minute project uses phase 0, 10 or
20; stagger repositories across those phases. Verify the actual workflow filename
and grant that repository Actions write access in the existing fine-grained token.
Store the token only as the Cloudflare secret GITHUB_ACTIONS_TOKEN.

Do not deploy this empty example over a live shared Worker. Preserve every current
project registration, Worker identity and secret. A configuration file or a passing
unit test does not prove production dispatch works: check Cloudflare logs and the
actual manual/scheduled Actions runs after an authorized deployment.

Run the offline tests with `node --test tests/*.test.mjs` from this directory.
