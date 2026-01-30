## Capacitor wrapping (single codebase)

1) Build/copy web assets:
- Copy `../frontend/*` into `./dist/` (or implement `copy-web.js`).

2) Install:
- npm i

3) Add Android:
- npx cap add android

4) Sync:
- npx cap sync

5) Open:
- npx cap open android

### Camera scanning
- Web PWA uses BarcodeDetector over getUserMedia (or swap in qr-scanner library offline).
- For native, add a BarcodeScanner plugin (recommended) and call it when `Capacitor.isNativePlatform()`.

### Geolocation
- Use `@capacitor/geolocation` in native fallback.
