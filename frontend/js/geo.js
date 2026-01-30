export async function getCoords() {
  // Capacitor fallback
  if (window.Capacitor?.isNativePlatform?.()) {
    try {
      const { Geolocation } = window.Capacitor.Plugins;
      const pos = await Geolocation.getCurrentPosition({ enableHighAccuracy: true, timeout: 10_000 });
      return { lat: pos.coords.latitude, lng: pos.coords.longitude };
    } catch {}
  }
  // Web
  if (!navigator.geolocation) throw new Error("Geolocation not available");
  return await new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(
      (p) => resolve({ lat: p.coords.latitude, lng: p.coords.longitude }),
      (e) => reject(new Error(e.message || "Geolocation error")),
      { enableHighAccuracy: true, timeout: 10_000 }
    );
  });
}
