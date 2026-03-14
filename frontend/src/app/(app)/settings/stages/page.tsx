"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { listStages, updateStage, reorderStages } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { ProjectStage } from "@/lib/types";

export default function StagesSettingsPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [stages, setStages] = useState<ProjectStage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getToken().then((t) => {
      if (!t) { router.push("/login"); return; }
      setToken(t);
      listStages(t).then((data: any) => { setStages(data); setLoading(false); });
    });
  }, [router]);

  async function handleNameChange(id: string, name: string) {
    setStages((prev) => prev.map((s) => s.id === id ? { ...s, name } : s));
  }

  async function saveStage(stage: ProjectStage) {
    await updateStage(stage.id, { name: stage.name, color: stage.color }, token);
  }

  async function moveUp(idx: number) {
    if (idx === 0) return;
    const reordered = [...stages];
    [reordered[idx - 1], reordered[idx]] = [reordered[idx], reordered[idx - 1]];
    const order = reordered.map((s, i) => ({ id: s.id, order_index: i + 1 }));
    setStages(reordered.map((s, i) => ({ ...s, order_index: i + 1 })));
    await reorderStages(order, token);
  }

  if (loading) return <div className="p-8 text-gray-500">Loading…</div>;

  return (
    <div className="p-6 max-w-xl">
      <h1 className="text-xl font-semibold mb-6">Pipeline Stages</h1>
      <div className="bg-white border rounded-lg divide-y">
        {stages.map((stage, idx) => (
          <div key={stage.id} className="flex items-center gap-3 px-4 py-3">
            <button onClick={() => moveUp(idx)} disabled={idx === 0} className="text-gray-300 hover:text-gray-600 disabled:opacity-0">↑</button>
            <input
              type="color"
              value={stage.color}
              onChange={(e) => setStages((prev) => prev.map((s) => s.id === stage.id ? { ...s, color: e.target.value } : s))}
              onBlur={() => saveStage(stage)}
              className="w-6 h-6 rounded cursor-pointer border-0"
            />
            <input
              type="text"
              value={stage.name}
              onChange={(e) => handleNameChange(stage.id, e.target.value)}
              onBlur={() => saveStage(stage)}
              className="flex-1 border-0 bg-transparent text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 rounded px-1"
            />
            <span className="text-xs text-gray-400">{stage.is_terminal ? "terminal" : ""}{stage.is_default ? "default" : ""}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
