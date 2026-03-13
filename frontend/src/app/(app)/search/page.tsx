"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { globalSearch } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import Link from "next/link";

export default function SearchPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [q, setQ] = useState("");
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getToken().then((t) => { if (!t) router.push("/login"); else setToken(t); });
  }, [router]);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!q.trim()) return;
    setLoading(true);
    const data = await globalSearch(q, token).catch(() => null);
    setResults(data);
    setLoading(false);
  }

  return (
    <div className="p-6 max-w-2xl">
      <h1 className="text-xl font-semibold mb-6">Search</h1>
      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input
          type="search"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search contacts, companies, projects…"
          className="flex-1 border rounded px-3 py-2 text-sm"
          autoFocus
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700">
          Search
        </button>
      </form>

      {loading && <p className="text-gray-500 text-sm">Searching…</p>}

      {results && (
        <div className="space-y-6">
          {results.contacts?.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold uppercase text-gray-400 mb-2">Contacts</h2>
              <div className="bg-white border rounded-lg divide-y">
                {results.contacts.map((c: any) => (
                  <Link key={c.id} href={`/contacts/${c.id}`} className="flex items-center gap-3 px-4 py-2 hover:bg-gray-50">
                    <div className="w-7 h-7 rounded-full bg-gray-200 flex items-center justify-center text-xs font-semibold">
                      {c.first_name?.[0]}{c.last_name?.[0] ?? ""}
                    </div>
                    <div>
                      <p className="text-sm font-medium">{c.first_name} {c.last_name}</p>
                      <p className="text-xs text-gray-400">{c.title} {c.email}</p>
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          )}
          {results.companies?.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold uppercase text-gray-400 mb-2">Companies</h2>
              <div className="bg-white border rounded-lg divide-y">
                {results.companies.map((c: any) => (
                  <Link key={c.id} href={`/companies/${c.id}`} className="flex items-center gap-3 px-4 py-2 hover:bg-gray-50">
                    <span className="text-sm">{c.name}</span>
                    {c.industry && <span className="text-xs text-gray-400">{c.industry}</span>}
                  </Link>
                ))}
              </div>
            </section>
          )}
          {results.projects?.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold uppercase text-gray-400 mb-2">Projects</h2>
              <div className="bg-white border rounded-lg divide-y">
                {results.projects.map((p: any) => (
                  <Link key={p.id} href={`/projects/${p.id}`} className="flex items-center gap-3 px-4 py-2 hover:bg-gray-50">
                    <span className="text-sm">{p.name}</span>
                    {p.stage_name && <span className="text-xs text-gray-400 ml-2">· {p.stage_name}</span>}
                  </Link>
                ))}
              </div>
            </section>
          )}
          {results.contacts?.length === 0 && results.companies?.length === 0 && results.projects?.length === 0 && (
            <p className="text-sm text-gray-400">No results for "{q}".</p>
          )}
        </div>
      )}
    </div>
  );
}
