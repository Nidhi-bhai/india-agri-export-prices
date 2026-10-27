# India Agri Export Price Index

Free, weekly reference prices for Indian agri exports: moringa, ashwagandha, neem, curry leaf, indigo, wheatgrass, turmeric, jaggery, millets (ragi, bajra, foxtail, kodo, little, proso, barnyard, browntop), khapli wheat, cold-pressed groundnut / coconut / karanja / moringa-seed oils and vetiver root.

**Live site:** https://nidhi-bhai.github.io/india-agri-export-prices/

- **Sources:** UN Comtrade (India monthly exports by HS code → USD/kg unit value; annual top destinations), Agmarknet (Govt. of India all-India average mandi prices, INR/quintal), ECB USD/INR via frankfurter.dev, plus clearly labelled desk estimates with links.
- **Every number carries its source and date.** Gaps stay empty; nothing is interpolated or invented.
- **History:** `docs/data/history.csv` is append-only; a GitHub Actions job adds a snapshot every Monday.
- **Downloads:** [latest.csv](https://nidhi-bhai.github.io/india-agri-export-prices/data/latest.csv) · [latest.json](https://nidhi-bhai.github.io/india-agri-export-prices/data/latest.json) · [history.csv](https://nidhi-bhai.github.io/india-agri-export-prices/data/history.csv)
- **Methodology:** https://nidhi-bhai.github.io/india-agri-export-prices/methodology.html

Run locally: `python scripts/fetch.py && python scripts/build.py` (Python 3, standard library only, no API keys).

Published by Nidhi Farms, a sourcing firm (trader, not a grower) in Andhra Pradesh, India. Conventional grade. Quotes and samples: nidhi69n@gmail.com.

Data: CC BY 4.0 (official series remain subject to their publishers' terms). Code: MIT.
