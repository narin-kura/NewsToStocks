# MarketSignal — Android App Build Guide

The mobile app is an [Expo](https://expo.dev) (React Native) app using Expo Router.
It consumes the JSON API added to the Flask backend (`/api/signals`, `/api/search`,
`/api/tabs`). This guide produces an **installable Android APK** via **EAS Build**
(Expo's cloud build — no Android Studio needed).

---

## 0. One value you MUST set first

Open [`app.json`](./app.json) and replace the API URL placeholder with the real
**Cloud Run** URL of the NewsToStocks backend:

```json
"extra": {
  "apiUrl": "https://REPLACE-WITH-NEWSTOSTOCKS-CLOUD-RUN-URL"
}
```

Get it from **GCP Console → Cloud Run → `newstostocks` → URL** (or the "Show service
URL" step of the last `Deploy to Cloud Run (GCP)` GitHub Action). It looks like
`https://newstostocks-xxxxxxxxxx-uc.a.run.app`.

> The app uses **Cloud Run**, not the Hugging Face Space. You can override per-build
> with the `EXPO_PUBLIC_API_URL` env var.

---

## 1. Prerequisites (one-time)

```bash
npm install -g eas-cli      # or use npx eas-cli@latest below
eas login                   # free Expo account (expo.dev/signup)
```

## 2. Install deps & link to EAS

```bash
cd mobile
npm install
eas init                    # links an EAS project, writes extra.eas.projectId
```

## 3. Build the APK

```bash
eas build --platform android --profile preview
```

`preview` (see [`eas.json`](./eas.json)) outputs an **APK** for internal distribution.
When the cloud build finishes you get a download URL. Let EAS manage the Android
keystore on first run.

## 4. Install on a phone

- Open the build URL on the device and download the `.apk`, or
- `eas build:run -p android` to install to a connected device/emulator.
- Allow "Install unknown apps" for your browser/file manager.

---

## Screens

| Tab | What it shows |
|---|---|
| **Signals** | Ranked stock signals by sector (chips) + sort (Top Picks / Gainers / Losers / A–Z), pull to refresh |
| **Search** | Look up any ticker/company → sentiment + linked articles |
| **About** | How it works + disclaimer |
| Stock detail | Positive & negative coverage with tappable article links, live price |

## Profiles in `eas.json`

| Profile | Output | Use for |
|---|---|---|
| `development` | APK + dev client | live-reload debugging |
| `preview` | APK | **share with testers** (sideload) |
| `production` | AAB | Google Play submission ($25 one-time) |

## Quick local preview (no build)

```bash
cd mobile
EXPO_PUBLIC_API_URL=https://<cloud-run-url> npx expo start   # scan QR with Expo Go
```
