"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { listMergeSuggestions, triggerMergeScan, resolvesuggestion, mergeContacts, getContact } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { MergeSuggestion, Contact } from "@/lib/types";

export default function MergePage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [suggestions, setSuggestions] = useState<MergeSuggestion[]>([]);
  const [contacts, setContacts] = useState<Record<string, Contact>>({});
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  useEffect(() => {
    getToken().then((t) => {
      if (!t) { router.push("/login"); return; }
      setToken(t);
      loadSuggestions(t);
    });
  }, [router]);

  async function loadSuggestions(t: string) {
    const data: any = await listMergeSuggestions(t);
    setSuggestions(data);
    // Load contact details
    const ids = new Set<string>();
    data.forEach((s: MergeSuggestion) => { ids.add(s.contact_a_id); ids.add(s.contact_b_id); });
    const entries = await Promise.all(
      Array.from(ids).map((id) => getContact(id, t).then((c: any) => [id, c]))
    );
    setContacts(Object.fromEntries(entries));
    setLoading(false);
  }

  async function scan() {
    setScanning(true);
    await triggerMergeScan(token);
    setTimeout(() => { loadSuggestions(token); setScanning(false); }, 3000);
  }

  async function reject(id: string) {
    await resolvesuggestion(id, "rejected", token);
    setSuggestions((prev) => prev.filter((s) => s.id !== id));
  }

  async function merge(suggestion: MergeSuggestion) {
    await mergeContacts(suggestion.contact_a_id, suggestion.contact_b_id, {}, token);
    setSuggestions((prev) => prev.filter((s) => s.id !== suggestion.id));
  }

  if (loading) return <div className="p-8 text-gray-500">Loading…</div>;

  return (
    <div className="p-6 max-w-2xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold">Merge Suggestions</h1>
        <button onClick={scan} disabled={scanning} className="border px-4 py-2 rounded text-sm hover:bg-gray-50 disabled:opacity-50">
          {scanning ? "Scanning…" : "Scan for duplicates"}
        </button>
      </div>
      {suggestions.length === 0 && (
        <p className="text-sm text-gray-400">No pending merge suggestions. Click "Scan" to find duplicates.</p>
      )}
      <div className="space-y-4">
        {suggestions.map((s) => {
          const a = contacts[s.contact_a_id];
          const b = contacts[s.contact_b_id];
          const reasons = s.reasons ? JSON.parse(s.reasons) : [];
          return (
            <div key={s.id} className="bg-white border rounded-lg p-4">
              <div className="flex items-center gap-4 mb-3">
                <div className="flex-1">
                  <p className="text-sm font-medium">{a?.first_name} {a?.last_name}</p>
                  <p className="text-xs text-gray-400">{a?.email}</p>
                </div>
                <div className="text-gray-400 text-sm">=</div>
                <div className="flex-1 text-right">
                  <p className="text-sm font-medium">{b?.first_name} {b?.last_name}</p>
                  <p className="text-xs text-gray-400">{b?.email}</p>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs text-gray-500">
                    Confidence: {(s.confidence_score * 100).toFixed(0)}% · {reasons.join(", ")}
                  </span>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => reject(s.id)} className="text-xs border px-3 py-1 rounded hover:bg-gray-50">Reject</button>
                  <button onClick={() => merge(s)} className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
                    Merge →
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
