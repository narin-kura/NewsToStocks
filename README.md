---
title: MarketSignal — Financial News Intelligence
sdk: docker
colorFrom: blue
colorTo: green
pinned: true
---

# MarketSignal 📈
*formerly NewsToStocks*

[![Website](https://img.shields.io/badge/Live%20App-marketsignal.vigyatri.com-blue?style=flat-square&logo=google-chrome)](https://marketsignal.vigyatri.com)
[![Hugging Face](https://img.shields.io/badge/Mirror-Hugging%20Face-gray?style=flat-square&logo=huggingface)](https://knnarin-newstostocks.hf.space)
[![Google Cloud Run](https://img.shields.io/badge/Powered%20by-GCP%20Cloud%20Run-gray?style=flat-square&logo=google-cloud)](https://newstostocks-h5axc6napq-uc.a.run.app/)

AI-powered financial news intelligence — scans 15+ live sources every 15 minutes, runs sentiment analysis, and surfaces stocks with the strongest positive momentum across 25 market sectors.

**For educational purposes only — not financial advice.**

## Features
- Live news scanning from Reuters, CNBC, WSJ, MarketWatch and 15+ sources
- TextBlob sentiment analysis across 25 market sectors
- S&P 500 + NASDAQ stock coverage
- Custom RSS feed support
- Watchlist — save stocks to track (sign in required)
- Saved feeds — persist custom sources across sessions (sign in required)

## Deployment
Built with Flask, deployed on Hugging Face Spaces and GCP Cloud Run via GitHub Actions.

## Usage
1. Pick a sector from the sidebar to filter results
2. Add a custom RSS feed to scan additional sources
3. Sign in to save your watchlist and custom feeds across sessions

---