"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createProject, listStages } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { ProjectStage } from "@/lib/types";

export default function NewProjectPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [stages, setStages] = useState<ProjectStage[]>([]);
  const [form, setForm] = useState({
    name: "", description: "", stage_id: "", value_estimate: "",
    currency: "USD", close_date_target: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getToken().then((t) => {
      if (!t) { router.push("/login"); return; }
      setToken(t);
      listStages(t).then((data: any) => {
        setStages(data);
        const defaultStage = data.find((s: ProjectStage) => s.is_default);
        if (defaultStage) setForm((f) => ({ ...f, stage_id: defaultStage.id }));
      });
    });
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = {
        ...form,
        value_estimate: form.value_estimate ? Number(form.value_estimate) : null,
        close_date_target: form.close_date_target || null,
      };
      const project: any = await createProject(payload, token);
      router.push(`/projects/${project.id}`);
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-xl">
      <h1 className="text-xl font-semibold mb-6">New Project</h1>
      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Project name *</label>
          <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full border rounded px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Stage</label>
          <select value={form.stage_id} onChange={(e) => setForm({ ...form, stage_id: e.target.value })} className="w-full border rounded px-3 py-2 text-sm">
            <option value="">None</option>
            {stages.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Value estimate</label>
            <input type="number" step="0.01" value={form.value_estimate} onChange={(e) => setForm({ ...form, value_estimate: e.target.value })} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Currency</label>
            <input value={form.currency} onChange={(e) => setForm({ ...form, currency: e.target.value })} className="w-full border rounded px-3 py-2 text-sm" maxLength={3} />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Target close date</label>
          <input type="date" value={form.close_date_target} onChange={(e) => setForm({ ...form, close_date_target: e.target.value })} className="w-full border rounded px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={3} className="w-full border rounded px-3 py-2 text-sm resize-y" />
        </div>
        <div className="flex gap-3">
          <button type="submit" disabled={loading} className="bg-blue-600 text-white px-6 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {loading ? "Saving…" : "Create project"}
          </button>
          <button type="button" onClick={() => router.back()} className="border px-6 py-2 rounded text-sm font-medium hover:bg-gray-50">Cancel</button>
        </div>
      </form>
    </div>
  );
}
