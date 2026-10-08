import { useEffect, useState, useCallback } from 'react';

type ComparePoint = { step: number; adaptive: number; fixed: number; throughputAdaptive: number; throughputFixed: number };
type HeatmapRow = { junction: string; id: string; hours: number[] };
type Recommendation = { id: number; junction_id: string; issue_type: string; severity: string; description: string; suggested_action: string; status: string };

const BASE = 'http://localhost:8000';

export function useAnalytics() {
  const [compareData, setCompareData] = useState<Record<string, ComparePoint[]>>({});
  const [heatmap, setHeatmap] = useState<HeatmapRow[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch fixed vs adaptive comparison for a junction
  const fetchCompare = useCallback(async (junctionId: string) => {
    if (compareData[junctionId]) return;
    try {
      const res = await fetch(BASE + '/api/metrics/compare/' + junctionId);
      if (res.ok) {
        const data = await res.json();
        const points: ComparePoint[] = (data.comparison || []).map((row: any, i: number) => ({
          step: i,
          adaptive: row.adaptive_wait ?? row.adaptive_avg_wait ?? 0,
          fixed: row.fixed_wait ?? row.fixed_avg_wait ?? 0,
          throughputAdaptive: row.adaptive_throughput ?? 0,
          throughputFixed: row.fixed_throughput ?? 0,
        }));
        setCompareData(prev => ({ ...prev, [junctionId]: points }));
      }
    } catch (e) {
      // Fallback mock
      const pts: ComparePoint[] = Array.from({ length: 20 }, (_, i) => ({
        step: i,
        adaptive: 35 + Math.sin(i / 3) * 12 + i * 0.5,
        fixed: 62 + Math.sin(i / 2.5) * 8 + i * 0.3,
        throughputAdaptive: 2800 + i * 40 + Math.sin(i) * 200,
        throughputFixed: 2100 + i * 20 + Math.sin(i) * 150,
      }));
      setCompareData(prev => ({ ...prev, [junctionId]: pts }));
    }
  }, [compareData]);

  // Fetch heatmap
  useEffect(() => {
    async function loadHeatmap() {
      try {
        const res = await fetch(BASE + '/api/analytics/heatmap');
        if (res.ok) {
          const data = await res.json();
          // data expected: { junctions: [{id, name, hourly: [24 numbers]}] }
          if (data.junctions) {
            setHeatmap(data.junctions.map((j: any) => ({
              junction: j.name.length > 20 ? j.name.slice(0, 18) + '..' : j.name,
              id: j.id,
              hours: j.hourly || Array.from({ length: 24 }, (_, h) => Math.round(20 + Math.sin((h - 8) / 3) * 30 + Math.random() * 10)),
            })));
          } else {
            throw new Error('no data');
          }
        } else throw new Error('non-ok');
      } catch {
        // Mock heatmap using typical Surat traffic pattern
        const junctions = ['Udhna Darwaja','Delhi Gate','Majura Gate','Sahara Darwaja','Athwa Gate','Varachha','Station Circle'];
        setHeatmap(junctions.map((name, ji) => ({
          junction: name,
          id: 'JN-0' + (ji + 1),
          hours: Array.from({ length: 24 }, (_, h) => {
            // Morning peak 8-10, Evening peak 17-20
            const morning = h >= 8 && h <= 10 ? 80 + (ji * 5 % 15) : 0;
            const evening = h >= 17 && h <= 20 ? 85 + (ji * 7 % 12) : 0;
            const base = 15 + (ji * 3 % 20);
            return Math.min(100, Math.round(base + morning + evening + Math.sin((h + ji) / 2) * 8));
          }),
        })));
      }
      setLoading(false);
    }
    loadHeatmap();
    const id = setInterval(loadHeatmap, 60000);
    return () => clearInterval(id);
  }, []);

  // Fetch recommendations
  useEffect(() => {
    async function loadRecs() {
      try {
        const res = await fetch(BASE + '/api/recommendations');
        if (res.ok) {
          const data = await res.json();
          setRecommendations(Array.isArray(data) ? data : []);
        }
      } catch { /* use empty */ }
    }
    loadRecs();
    const id = setInterval(loadRecs, 15000);
    return () => clearInterval(id);
  }, []);

  const updateRecStatus = useCallback(async (id: number, status: string) => {
    try {
      await fetch(BASE + '/api/recommendations/' + id + '/status', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      setRecommendations(prev => prev.map(r => r.id === id ? { ...r, status } : r));
    } catch {}
  }, []);

  return { compareData, fetchCompare, heatmap, recommendations, updateRecStatus, loading };
}
