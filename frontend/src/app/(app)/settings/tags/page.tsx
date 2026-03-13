"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { listTags, createTag, deleteTag } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { Tag } from "@/lib/types";

export default function TagsSettingsPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [tags, setTags] = useState<Tag[]>([]);
  const [newName, setNewName] = useState("");
  const [newColor, setNewColor] = useState("#6B7280");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getToken().then((t) => {
      if (!t) { router.push("/login"); return; }
      setToken(t);
      listTags(t).then((data: any) => { setTags(data); setLoading(false); });
    });
  }, [router]);

  async function addTag(e: React.FormEvent) {
    e.preventDefault();
    const tag: any = await createTag({ name: newName, color: newColor }, token);
    setTags((prev) => [...prev, tag]);
    setNewName("");
  }

  async function removeTag(id: string) {
    await deleteTag(id, token);
    setTags((prev) => prev.filter((t) => t.id !== id));
  }

  if (loading) return <div className="p-8 text-gray-500">Loading…</div>;

  return (
    <div className="p-6 max-w-xl">
      <h1 className="text-xl font-semibold mb-6">Tags</h1>
      <form onSubmit={addTag} className="flex gap-2 mb-6">
        <input type="color" value={newColor} onChange={(e) => setNewColor(e.target.value)} className="w-9 h-9 rounded border cursor-pointer" />
        <input
          type="text"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="New tag name…"
          required
          className="flex-1 border rounded px-3 py-2 text-sm"
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded text-sm hover:bg-blue-700">Add</button>
      </form>
      <div className="bg-white border rounded-lg divide-y">
        {tags.map((tag) => (
          <div key={tag.id} className="flex items-center gap-3 px-4 py-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: tag.color }} />
            <span className="flex-1 text-sm">{tag.name}</span>
            <button onClick={() => removeTag(tag.id)} className="text-xs text-red-500 hover:text-red-700">Remove</button>
          </div>
        ))}
        {tags.length === 0 && <p className="px-4 py-6 text-center text-sm text-gray-400">No tags yet.</p>}
      </div>
    </div>
  );
}
