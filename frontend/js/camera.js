export async function startCamera(videoEl) {
  // Capacitor camera plugins will be used for still capture later (BarcodeScanner plugins exist too),
  // but for PWA scanning we prefer live video.
  const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
  videoEl.srcObject = stream;
  await videoEl.play();
  return () => stream.getTracks().forEach(t => t.stop());
}
