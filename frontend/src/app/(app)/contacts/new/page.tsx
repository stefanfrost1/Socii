"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createContact } from "@/lib/api";
import { getToken } from "@/lib/supabase";

export default function NewContactPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [form, setForm] = useState({
    first_name: "", last_name: "", email: "", phone: "", title: "",
    linkedin_url: "", twitter_url: "", github_url: "", website_url: "",
    address_city: "", address_country: "", bio_notes: "", contact_frequency_days: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getToken().then((t) => { if (!t) router.push("/login"); else setToken(t); });
  }, [router]);

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm({ ...form, [field]: e.target.value });

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = { ...form, contact_frequency_days: form.contact_frequency_days ? Number(form.contact_frequency_days) : null };
      const contact: any = await createContact(payload, token);
      router.push(`/contacts/${contact.id}`);
    } catch (err: any) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div className="p-6 max-w-2xl">
      <h1 className="text-xl font-semibold mb-6">New Contact</h1>
      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">First name *</label>
            <input required value={form.first_name} onChange={set("first_name")} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Last name</label>
            <input value={form.last_name} onChange={set("last_name")} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input type="email" value={form.email} onChange={set("email")} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Phone</label>
            <input value={form.phone} onChange={set("phone")} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Job title</label>
          <input value={form.title} onChange={set("title")} className="w-full border rounded px-3 py-2 text-sm" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">LinkedIn URL</label>
            <input value={form.linkedin_url} onChange={set("linkedin_url")} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Twitter / X URL</label>
            <input value={form.twitter_url} onChange={set("twitter_url")} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">GitHub URL</label>
            <input value={form.github_url} onChange={set("github_url")} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Website</label>
            <input value={form.website_url} onChange={set("website_url")} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">City</label>
            <input value={form.address_city} onChange={set("address_city")} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Country</label>
            <input value={form.address_country} onChange={set("address_country")} className="w-full border rounded px-3 py-2 text-sm" />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Contact every (days)</label>
          <input type="number" min="1" value={form.contact_frequency_days} onChange={set("contact_frequency_days")} className="w-32 border rounded px-3 py-2 text-sm" placeholder="e.g. 30" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Bio / notes</label>
          <textarea value={form.bio_notes} onChange={set("bio_notes")} rows={3} className="w-full border rounded px-3 py-2 text-sm resize-y" />
        </div>
        <div className="flex gap-3">
          <button type="submit" disabled={loading} className="bg-blue-600 text-white px-6 py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50">
            {loading ? "Saving…" : "Create contact"}
          </button>
          <button type="button" onClick={() => router.back()} className="border px-6 py-2 rounded text-sm font-medium hover:bg-gray-50">Cancel</button>
        </div>
      </form>
    </div>
  );
}
