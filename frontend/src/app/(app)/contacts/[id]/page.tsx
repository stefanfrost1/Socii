"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getContact, getContactTimeline, searchImageCandidates, importContactImage } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { Contact, Interaction } from "@/lib/types";
import { timeAgo, interactionTypeIcon, neglectEmoji, neglectScore } from "@/lib/utils";
import Link from "next/link";

export default function ContactDetailPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  const [token, setToken] = useState("");
  const [contact, setContact] = useState<Contact | null>(null);
  const [timeline, setTimeline] = useState<Interaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [imageCandidates, setImageCandidates] = useState<string[]>([]);
  const [searchingImage, setSearchingImage] = useState(false);

  useEffect(() => {
    getToken().then((t) => {
      if (!t) { router.push("/login"); return; }
      setToken(t);
      Promise.all([getContact(id, t), getContactTimeline(id, t)]).then(([c, tl]: any[]) => {
        setContact(c);
        setTimeline(tl);
        setLoading(false);
      });
    });
  }, [id, router]);

  async function handleImageSearch() {
    setSearchingImage(true);
    try {
      const result: any = await searchImageCandidates(id, token);
      setImageCandidates(result.candidates ?? []);
    } finally {
      setSearchingImage(false);
    }
  }

  async function handleImportImage(url: string) {
    const result: any = await importContactImage(id, url, token);
    setContact((prev) => prev ? { ...prev, image_url: result.image_url } : prev);
    setImageCandidates([]);
  }

  if (loading) return <div className="p-8 text-gray-500">Loading…</div>;
  if (!contact) return <div className="p-8 text-red-600">Not found</div>;

  const score = neglectScore(contact.last_contacted_at, contact.contact_frequency_days);

  return (
    <div className="p-6 max-w-4xl">
      <div className="flex items-start gap-4 mb-6">
        <div className="relative">
          {contact.image_url ? (
            <img src={contact.image_url} alt="" className="w-16 h-16 rounded-full object-cover" />
          ) : (
            <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center text-xl font-semibold text-gray-600">
              {contact.first_name[0]}{contact.last_name?.[0] ?? ""}
            </div>
          )}
          <button
            onClick={handleImageSearch}
            disabled={searchingImage}
            title="Search for profile image"
            className="absolute -bottom-1 -right-1 bg-white border rounded-full p-0.5 text-xs hover:bg-gray-50"
          >
            {searchingImage ? "…" : "🔍"}
          </button>
        </div>

        <div className="flex-1">
          <h1 className="text-2xl font-semibold">{contact.first_name} {contact.last_name}</h1>
          {contact.title && <p className="text-gray-500">{contact.title}</p>}
          <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
            {contact.email && <span>{contact.email}</span>}
            {contact.phone && <span>{contact.phone}</span>}
          </div>
          <div className="flex items-center gap-2 mt-2">
            <span>{neglectEmoji(score)}</span>
            {contact.last_contacted_at ? (
              <span className="text-sm text-gray-500">Last contacted {timeAgo(contact.last_contacted_at)}</span>
            ) : (
              <span className="text-sm text-gray-400">Never contacted</span>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <Link href={`/interactions/new?contact=${id}`} className="bg-blue-600 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-700">
            Log Interaction
          </Link>
          <Link href={`/contacts/${id}/edit`} className="border px-3 py-1.5 rounded text-sm hover:bg-gray-50">
            Edit
          </Link>
        </div>
      </div>

      {/* Image picker modal */}
      {imageCandidates.length > 0 && (
        <div className="mb-6 p-4 border rounded-lg bg-yellow-50">
          <p className="text-sm font-medium mb-3">Select a profile image:</p>
          <div className="flex gap-3 flex-wrap">
            {imageCandidates.map((url, i) => (
              <button key={i} onClick={() => handleImportImage(url)} className="hover:ring-2 ring-blue-500 rounded overflow-hidden">
                <img src={url} alt="" className="w-16 h-16 object-cover rounded" />
              </button>
            ))}
          </div>
          <button onClick={() => setImageCandidates([])} className="mt-2 text-xs text-gray-400 hover:text-gray-600">
            Cancel
          </button>
        </div>
      )}

      {/* Social links */}
      <div className="flex gap-3 mb-6 flex-wrap">
        {contact.linkedin_url && <a href={contact.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-xs border px-3 py-1 rounded hover:bg-gray-50">LinkedIn</a>}
        {contact.twitter_url && <a href={contact.twitter_url} target="_blank" rel="noopener noreferrer" className="text-xs border px-3 py-1 rounded hover:bg-gray-50">Twitter</a>}
        {contact.github_url && <a href={contact.github_url} target="_blank" rel="noopener noreferrer" className="text-xs border px-3 py-1 rounded hover:bg-gray-50">GitHub</a>}
        {contact.website_url && <a href={contact.website_url} target="_blank" rel="noopener noreferrer" className="text-xs border px-3 py-1 rounded hover:bg-gray-50">Website</a>}
      </div>

      {/* Bio */}
      {contact.bio_notes && (
        <div className="mb-6 bg-white border rounded-lg p-4">
          <h2 className="text-sm font-medium text-gray-600 mb-2">Notes</h2>
          <p className="text-sm text-gray-800 whitespace-pre-wrap">{contact.bio_notes}</p>
        </div>
      )}

      {/* Timeline */}
      <div className="bg-white border rounded-lg p-4">
        <h2 className="text-sm font-semibold text-gray-700 mb-4">Timeline ({timeline.length})</h2>
        {timeline.length === 0 && (
          <p className="text-sm text-gray-400">No interactions logged yet.</p>
        )}
        <div className="space-y-3">
          {timeline.map((interaction) => (
            <Link
              key={interaction.id}
              href={`/interactions/${interaction.id}`}
              className="block hover:bg-gray-50 rounded p-2 -mx-2"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">
                  {interactionTypeIcon(interaction.interaction_type)} {interaction.interaction_type}
                </span>
                <span className="text-xs text-gray-400">{timeAgo(interaction.interaction_date)}</span>
              </div>
              <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">{interaction.raw_content.slice(0, 120)}</p>
              <span className={`text-xs ${interaction.ai_status === "done" ? "text-green-600" : interaction.ai_status === "failed" ? "text-red-500" : "text-gray-400"}`}>
                {interaction.ai_status === "done" ? "✓ AI summary" : interaction.ai_status === "pending" ? "processing…" : interaction.ai_status}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
