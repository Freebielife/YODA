# TON Observatory foundation 1.2.0

This independent repository is the canonical factory. Its reference/ directory
is a frozen local source snapshot. No live Ludoman source, HTML or data is fetched
during generation. KITO and all existing sites are outside this migration.

## Create from a token contract

From the factory repository:

```bash
python3 -m scripts.discover_project \
  --token TOKEN_CONTRACT \
  --github OWNER/REPOSITORY \
  --channel https://t.me/PROJECT_CHANNEL \
  --flag-file /absolute/path/to/approved-emoji.webp \
  --output /absolute/path/to/new-site
```

The generator checks the mainnet address CRC, reads metadata from TonAPI,
discovers native TON pools through GeckoTerminal, and requires a successful
matching TON swap in the candidate pool's TonAPI event feed. It chooses the
largest indexed USD liquidity among supported, swap-verified pools as the primary
chart source. This is indexed event evidence, not an independent contract audit.

The official hero logo is downloaded from token metadata, with `--website` for
fallback logo and channel discovery from the project's website. The section flag
must be explicitly selected with one of `--flag-key`, `--flag-file`, `--flag-emoji`.
A missing logo, channel or flag blocks setup and identifies the required input.
See BRANDING_STANDARD.md. It generates sources and project.json, refreshes on-chain sections, builds
index.html and verifies the bundle. `--prepare-only` skips collection/build.
Only native TON pairs on STON.fi and DeDust are supported by the trade collector.
Other discovered pairs may be listed separately; their swaps are not claimed as
covered by the main feed. A missing supported pair stops automatic creation.
Inactive pools without recent swap evidence need an explicit reviewed config.
Non-ASCII metadata names and symbols outside the accepted format also require
an explicit display configuration; names are never guessed or silently changed.

`--github` is the destination for future snapshot retrieval. Repository creation,
permissions and adding the project to the existing Cloudflare runner remain
separate deployment steps. This command does not create repositories, grant
permissions, deploy Workers or publish TON Storage bags.

## Per-project settings

`project.json` carries token identity, decimals, pools, primary chart pool,
optional links/artwork/custom badge criteria, service attributions, methodology,
engine version and size budget. It is the generation specification. To switch
contracts/pools/precision, regenerate into an empty directory. Changing just the
contract in a previously populated snapshot is deliberately rejected.

No project-specific NFT, staking or promotional labels are inherited. The shared
OG, Fragment +888, four-digit .ton and burn labels remain available. Burn checks,
DNS ownership, Fragment ownership and account classification use the existing
verified collectors; unavailable proofs are not fabricated.

Known custodial labels come from the curated shared registry. Two additional
Binance/Bybit address attributions supplied by the user are stored separately in
service-overrides.json with their actual provenance. They are not represented as
independently verified ownership. Exact contract interfaces distinguish pools,
routers and vaults; unnamed active non-wallet contracts remain generic contracts.
Service/contract entries are excluded from ordinary holder and seller rankings.
Unverified accounts can remain until the incremental classification queue reaches
them; the engine never claims every account has already been classified.

## UI and data integrity

- Show 10 ordinary holders, expand by the chevron to top 20, collapse back to 10.
  Collector sample remains 100 so service filtering does not truncate it to ten.
- Reuse the existing responsive design and RU/EN controls.
- Show per-section source timestamps/errors under a collapsible freshness detail.
- Flag main data older than 60 minutes; configured dispatch interval is 30 minutes.
- Retain prior verified sections on source failures; show unavailable rather than
  fabricated zero or empty activity. Partial badge errors remain visible.
- Keep bounded resumable swap backfill separate from current refresh. No invented
  week of history. Capitalization is last primary-pool swap price times CURRENT
  total supply, including locked tokens; not circulating market capitalization.
- Validate token/schema and configured pool identity before saving snapshots and
  before replacing HTML. Canonical address comparison accepts bounceable,
  non-bounceable and raw forms of the same mainnet basechain address.
- Assemble and validate HTML before atomic replacement. Default budget is
  2,500,000 UTF-8 bytes, explicitly configurable between 250,000 and 5,000,000.
  This is a project guardrail, not a claimed browser or TON Storage limit.
  Print the total/payload/image/source breakdown and save build/report.json.
- Reject external rendering scripts, styles, images and CSS URLs in the packaged
  HTML. Network calls are still used for fresh snapshots and manual wallet lookup.

## Verification

Run root Python regression tests, JS loader/chart tests, and generated-project
build/verify checks. UI acceptance: 10 -> 20 -> 10, RU/EN, no horizontal overflow
at 360/390/768/1280 iframe widths, valid navigation and self-contained resources.
Test addresses/balances used for responsive QA are synthetic and must never be
published as on-chain data.

## Rollout

Changes are limited to the shared factory and its new helpers. Existing token
sites require an explicit later migration; their HTML and data are not replaced.
Track ENGINE_VERSION/project.json for generated sites. Pilot changes on one
isolated output before applying to further projects.
