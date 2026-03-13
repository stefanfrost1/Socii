"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { listCompanies } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { Company } from "@/lib/types";
import Link from "next/link";

export default function CompaniesPage() {
  const router = useRouter();
  const [companies, setCompanies] = useState<Company[]>([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getToken().then((t) => {
      if (!t) { router.push("/login"); return; }
      listCompanies({}, t).then((data: any) => { setCompanies(data); setLoading(false); });
    });
  }, [router]);

  const filtered = q ? companies.filter((c) => c.name.toLowerCase().includes(q.toLowerCase())) : companies;

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold">Companies</h1>
        <Link href="/companies/new" className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700">
          + New Company
        </Link>
      </div>
      <input
        type="search"
        placeholder="Search companies…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="w-full border rounded px-3 py-2 text-sm mb-4"
      />
      {loading ? (
        <p className="text-gray-500">Loading…</p>
      ) : (
        <div className="bg-white rounded-lg border divide-y">
          {filtered.map((c) => (
            <Link key={c.id} href={`/companies/${c.id}`} className="flex items-center gap-4 px-4 py-3 hover:bg-gray-50">
              {c.logo_url ? (
                <img src={c.logo_url} alt="" className="w-8 h-8 rounded object-contain" />
              ) : (
                <div className="w-8 h-8 rounded bg-gray-200 flex items-center justify-center text-xs font-semibold text-gray-600">
                  {c.name[0]}
                </div>
              )}
              <div className="flex-1">
                <div className="font-medium text-sm">{c.name}</div>
                <div className="text-xs text-gray-400">{c.industry} {c.address_city ? `· ${c.address_city}` : ""}</div>
              </div>
            </Link>
          ))}
          {filtered.length === 0 && <p className="px-4 py-8 text-center text-sm text-gray-400">No companies found.</p>}
        </div>
      )}
    </div>
  );
}
