"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createInteraction, listContacts, listProjects } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { Contact, Project } from "@/lib/types";

const TYPES = ["email", "meeting", "call", "sms", "whatsapp", "linkedin", "other"];
const DIRECTIONS = ["inbound", "outbound", "mutual"];

export default function NewInteractionPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [form, setForm] = useState({
    contact_id: "",
    project_id: "",
    raw_content: "",
    interaction_type: "email",
    direction: "mutual",
    interaction_date: new Date().toISOString().slice(0, 16),
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getToken().then((t) => {
      if (!t) { router.push("/login"); return; }
      setToken(t);
      listContacts({}, t).then((data: any) => setContacts(data));
      listProjects({}, t).then((data: any) => setProjects(data));
    });
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const interaction: any = await createInteraction(
        { ...form, interaction_date: new Date(form.interaction_date).toISOString() },
        token
      );
      router.push(`/interactions/${interaction.id}`);
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-2xl">
      <h1 className="text-xl font-semibold mb-6">Log Interaction</h1>
      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Contact *</label>
          <select
            value={form.contact_id}
            onChange={(e) => setForm({ ...form, contact_id: e.target.value })}
            required
            className="w-full border rounded px-3 py-2 text-sm"
          >
            <option value="">Select contact…</option>
            {contacts.map((c) => (
              <option key={c.id} value={c.id}>
                {c.first_name} {c.last_name ?? ""}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Project (optional)</label>
          <select
            value={form.project_id}
            onChange={(e) => setForm({ ...form, project_id: e.target.value })}
            className="w-full border rounded px-3 py-2 text-sm"
          >
            <option value="">None</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-sm font-medium mb-1">Type</label>
            <select
              value={form.interaction_type}
              onChange={(e) => setForm({ ...form, interaction_type: e.target.value })}
              className="w-full border rounded px-3 py-2 text-sm"
            >
              {TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Direction</label>
            <select
              value={form.direction}
              onChange={(e) => setForm({ ...form, direction: e.target.value })}
              className="w-full border rounded px-3 py-2 text-sm"
            >
              {DIRECTIONS.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Date & time</label>
            <input
              type="datetime-local"
              value={form.interaction_date}
              onChange={(e) => setForm({ ...form, interaction_date: e.target.value })}
              className="w-full border rounded px-3 py-2 text-sm"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">
            Notes / email / transcript *
          </label>
          <textarea
            value={form.raw_content}
            onChange={(e) => setForm({ ...form, raw_content: e.target.value })}
            required
            rows={12}
            placeholder="Paste the email, notes, or transcript here. Claude will extract a business summary and action points automatically."
            className="w-full border rounded px-3 py-2 text-sm font-mono resize-y"
          />
          <p className="text-xs text-gray-400 mt-1">Minimum 20 characters · max ~6000 words</p>
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? "Saving…" : "Save & process with AI"}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="border px-6 py-2 rounded text-sm font-medium hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
