"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { listContacts } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { Contact } from "@/lib/types";
import { neglectEmoji, neglectScore, timeAgo } from "@/lib/utils";
import Link from "next/link";

export default function ContactsPage() {
  const router = useRouter();
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getToken().then((t) => {
      if (!t) { router.push("/login"); return; }
      listContacts({}, t).then((data: any) => {
        setContacts(data);
        setLoading(false);
      });
    });
  }, [router]);

  const filtered = q
    ? contacts.filter(
        (c) =>
          `${c.first_name} ${c.last_name ?? ""} ${c.email ?? ""}`.toLowerCase().includes(q.toLowerCase())
      )
    : contacts;

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold">Contacts</h1>
        <Link href="/contacts/new" className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700">
          + New Contact
        </Link>
      </div>
      <input
        type="search"
        placeholder="Search contacts…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        className="w-full border rounded px-3 py-2 text-sm mb-4"
      />
      {loading ? (
        <p className="text-gray-500">Loading…</p>
      ) : (
        <div className="bg-white rounded-lg border divide-y">
          {filtered.map((c) => {
            const score = neglectScore(c.last_contacted_at, c.contact_frequency_days);
            return (
              <Link key={c.id} href={`/contacts/${c.id}`} className="flex items-center gap-4 px-4 py-3 hover:bg-gray-50">
                {c.image_url ? (
                  <img src={c.image_url} alt="" className="w-8 h-8 rounded-full object-cover" />
                ) : (
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs font-semibold text-gray-600">
                    {c.first_name[0]}{c.last_name?.[0] ?? ""}
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm">{c.first_name} {c.last_name}</div>
                  <div className="text-xs text-gray-400 truncate">{c.title} {c.email}</div>
                </div>
                <div className="text-right">
                  <span className="text-sm">{neglectEmoji(score)}</span>
                  {c.last_contacted_at && (
                    <div className="text-xs text-gray-400">{timeAgo(c.last_contacted_at)}</div>
                  )}
                </div>
              </Link>
            );
          })}
          {filtered.length === 0 && (
            <p className="px-4 py-8 text-center text-sm text-gray-400">No contacts found.</p>
          )}
        </div>
      )}
    </div>
  );
}
