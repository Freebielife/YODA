# Baby Yoda Observatory

## О проекте / токене

Baby Yoda coin was born out of Egor's creativity and the imagination of the Telegram community. Its arrival resonates deeply with crypto enthusiasts, demonstrating the substantial impact even a modest token could have in the expansive world of blockchain.

Самоописание из метаданных токена; заявления проекта не проверены независимо.

Источники (проверены 2026-11-26):

- <https://tonapi.io/v2/jettons/EQC7vuKEYLdC72YhUWt3AUVA-Oi66Q1DxTHXH7r6pXaV50j7>

Generated from https://github.com/Freebielife/TON-Observatory-Template.

Run python3 -m scripts.refresh_observatory; python3 build.py; python3 verify.py.
Publish index.html in TON Sites only after independent on-chain verification.
The snapshot contains only data returned by collectors; unavailable sections remain explicitly marked.
Only native TON swap pairs supported. Locks, staking and custom project NFT badges are configured through project.json and verified against TonAPI.
GitHub Actions update workflow: `.github/workflows/update.yml`. Existing shared Cloudflare scheduler is managed externally; live dispatch is verified separately.

Foundation version: 1.3.0. Holders show 10, expandable to top 20.
`project.json` is the per-project specification. Contract/pool/precision changes require regenerating from the factory; do not reuse another token's snapshot.
Run `python3 build.py` for an atomic bundle and `build/report.json` size report.
No external fonts, scripts or images are needed to render the saved page. Fresh data checks and manual wallet lookups require network access.
Cloudflare dispatch registration and GitHub repository access remain separate deployment steps. No credentials go into HTML.

## YODA configuration

Contract: `0:bbbee28460b742ef6621516b77014540f8e8bae90d43c531d71fbafaa57695e7`. Decimals: 9. Metadata symbol: `Yoda`; UI symbol: `YODA`.

Foundation: 1.3.0, canonical template commit `65780137fa12eda7500f48d29c5b261411305274`.
Hero: user-supplied `image(20261125-173946).png`, used by explicit instruction instead of the metadata image. Provenance is recorded in project.json. Section flag: user-selected TONecoFlags #193, independently embedded.

Verified on 2026-11-26: exact token metadata and successful native TON swaps via TonAPI; pool discovery through GeckoTerminal. Primary chart source is the largest indexed supported swap-verified TON pool. Other quote tokens and unsupported DEX versions are outside the trade feed.

Project links from exact-contract metadata:

- https://babyyoda.lol
- https://t.me/BabyYodaTONCHAIN
- https://x.com/yodaonton

The saved HTML embeds interface scripts and images, with no external fonts. Fresh snapshots and wallet lookups need network access. Publication in main does not itself publish a TON Storage bag.

Link check on 2026-11-26: project website, configured DeDust/STON.fi pool pages and the gram.org token page returned HTTP 200. Telegram and X returned HTTP 403 from this environment, so their contents were not independently verified; their URLs match the exact-contract metadata.

Activity shows 20 rows, expandable to 50. Holders show 10, expandable to 20.
