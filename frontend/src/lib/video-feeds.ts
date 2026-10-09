// Real-time video mappings for 5 active camera footages (with cache-buster to ensure newly annotated lane borders load immediately)
const CACHE_KEY = "?v=lanes_live";

export const LIVE_FEEDS: Record<string, string> = {
  "JN-01": `/videos/traffic1.mp4${CACHE_KEY}`,
  "JN-02": `/videos/traffic2.mp4${CACHE_KEY}`,
  "JN-03": `/videos/traffic3.mp4${CACHE_KEY}`,
  "JN-04": `/videos/traffic4.mp4${CACHE_KEY}`,
  "JN-05": `/videos/traffic5.mp4${CACHE_KEY}`,
  "J001": `/videos/traffic1.mp4${CACHE_KEY}`,
  "J002": `/videos/traffic2.mp4${CACHE_KEY}`,
  "J003": `/videos/traffic3.mp4${CACHE_KEY}`,
  "J004": `/videos/traffic4.mp4${CACHE_KEY}`,
  "J005": `/videos/traffic5.mp4${CACHE_KEY}`,
  "CAM-U01": `/videos/traffic1.mp4${CACHE_KEY}`,
  "CAM-R02": `/videos/traffic2.mp4${CACHE_KEY}`,
  "CAM-A03": `/videos/traffic3.mp4${CACHE_KEY}`,
  "CAM-P04": `/videos/traffic4.mp4${CACHE_KEY}`,
  "CAM-V05": `/videos/traffic5.mp4${CACHE_KEY}`,
  "CAM-K06": `/videos/traffic6.mp4${CACHE_KEY}`,
  "CAM-T07": `/videos/traffic7.mp4${CACHE_KEY}`,
  "CAM-D08": `/videos/traffic8.mp4${CACHE_KEY}`,
  "CAM-M09": `/videos/traffic9.mp4${CACHE_KEY}`,
  "CAM-01": `/videos/traffic1.mp4${CACHE_KEY}`,
  "CAM-02": `/videos/traffic2.mp4${CACHE_KEY}`,
  "CAM-03": `/videos/traffic3.mp4${CACHE_KEY}`,
  "CAM-04": `/videos/traffic4.mp4${CACHE_KEY}`,
  "CAM-05": `/videos/traffic5.mp4${CACHE_KEY}`,
  "CAM-06": `/videos/traffic6.mp4${CACHE_KEY}`,
  "CAM-07": `/videos/traffic7.mp4${CACHE_KEY}`,
  "CAM-08": `/videos/traffic8.mp4${CACHE_KEY}`,
  "CAM-09": `/videos/traffic9.mp4${CACHE_KEY}`,
  "JN-09": `/videos/traffic9.mp4${CACHE_KEY}`,
  "J009": `/videos/traffic9.mp4${CACHE_KEY}`,
  "traffic9": `/videos/traffic9.mp4${CACHE_KEY}`,
};

export function getVideoForFeed(feed: { id?: string; junctionId?: string } | string | null | undefined): string | null {
  if (!feed) return null;
  const idStr = typeof feed === "string" ? feed : (feed.junctionId || feed.id || "");
  if (LIVE_FEEDS[idStr]) return LIVE_FEEDS[idStr];
  if (typeof feed !== "string") {
    if (feed.junctionId && LIVE_FEEDS[feed.junctionId]) return LIVE_FEEDS[feed.junctionId];
    if (feed.id && LIVE_FEEDS[feed.id]) return LIVE_FEEDS[feed.id];
  }
  const num = parseInt(idStr.replace(/\D/g, "") || "0", 10);
  if (num >= 1 && num <= 9) return `/videos/traffic${num}.mp4${CACHE_KEY}`;
  return null;
}
