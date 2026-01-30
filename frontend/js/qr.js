export async function scanQrFromVideo(videoEl, onResult) {
  // Minimal placeholder: attempt built-in BarcodeDetector if available.
  if (!videoEl) throw new Error("Video element missing");

  if (!("BarcodeDetector" in window)) {
    throw new Error("QR scan not supported in this browser. Enter code manually.");
  }

  const detector = new BarcodeDetector({ formats: ["qr_code"] });
  let active = true;
  let rafId = null;

  async function tick() {
    if (!active) return;
    try {
      const bitmap = await createImageBitmap(videoEl);
      const codes = await detector.detect(bitmap);
      if (codes && codes.length) {
        const raw = codes[0].rawValue || codes[0].data || "";
        if (raw) {
          onResult(raw);
          active = false;
          return;
        }
      }
    } catch {}
    rafId = requestAnimationFrame(tick);
  }

  rafId = requestAnimationFrame(tick);

  return () => {
    active = false;
    if (rafId) cancelAnimationFrame(rafId);
  };
}
