"use client";
import { useEffect, useState } from "react";
import { getDashboardOverview } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { DashboardOverview, Contact } from "@/lib/types";
import { timeAgo, neglectScore, neglectEmoji, interactionTypeIcon, sentimentColor } from "@/lib/utils";
import { differenceInDays, parseISO } from "date-fns";
import Link from "next/link";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getToken().then((token) => {
      if (!token) { window.location.href = "/login"; return; }
      getDashboardOverview(token)
        .then(setData)
        .catch((e) => setError(e.message));
    });
  }, []);

  if (error) return <div className="p-8 text-red-600">{error}</div>;
  if (!data) return <div className="p-8 text-gray-500">Loading…</div>;

  return (
    <div className="p-6">
      {/* Action bar */}
      <div className="flex gap-3 mb-6">
        <Link href="/interactions/new" className="bg-blue-600 text-white px-4 py-2 rounded text-sm font-medium hover:bg-blue-700">
          + Log Interaction
        </Link>
        <Link href="/contacts/new" className="border px-4 py-2 rounded text-sm font-medium hover:bg-gray-100">
          + New Contact
        </Link>
        <Link href="/projects/new" className="border px-4 py-2 rounded text-sm font-medium hover:bg-gray-100">
          + New Project
        </Link>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Recent Interactions */}
        <div className="col-span-1 bg-white rounded-lg border p-4">
          <h2 className="font-semibold text-sm text-gray-700 mb-3">Recent Interactions</h2>
          <div className="space-y-3">
            {data.recent_interactions.length === 0 && (
              <p className="text-sm text-gray-400">No interactions yet.</p>
            )}
            {data.recent_interactions.map(({ interaction, ai_summary }) => (
              <Link
                key={interaction.id}
                href={`/interactions/${interaction.id}`}
                className="block hover:bg-gray-50 rounded p-2 -mx-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">
                    {interactionTypeIcon(interaction.interaction_type)} Contact
                  </span>
                  <span className="text-xs text-gray-400">{timeAgo(interaction.interaction_date)}</span>
                </div>
                {ai_summary?.summary && (
                  <p className="text-xs text-gray-600 mt-1 line-clamp-2">{ai_summary.summary}</p>
                )}
                {interaction.ai_status === "pending" && (
                  <p className="text-xs text-gray-400 mt-1 italic">AI processing…</p>
                )}
              </Link>
            ))}
          </div>
        </div>

        {/* Pipeline */}
        <div className="col-span-1 bg-white rounded-lg border p-4">
          <h2 className="font-semibold text-sm text-gray-700 mb-3">Pipeline</h2>
          <div className="space-y-2">
            {data.pipeline.map(({ stage, count }) => (
              <div key={stage.id} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block w-2.5 h-2.5 rounded-full"
                    style={{ backgroundColor: stage.color }}
                  />
                  <span className="text-sm">{stage.name}</span>
                </div>
                <span className="text-sm font-semibold text-gray-600">{count}</span>
              </div>
            ))}
          </div>
          <Link href="/projects" className="block mt-4 text-xs text-blue-600 hover:underline">
            View Kanban →
          </Link>
        </div>

        {/* Needs Contact */}
        <div className="col-span-1 bg-white rounded-lg border p-4">
          <h2 className="font-semibold text-sm text-gray-700 mb-3">Needs Contact</h2>
          <div className="space-y-2">
            {data.needs_contact.length === 0 && (
              <p className="text-sm text-gray-400">All caught up!</p>
            )}
            {data.needs_contact.map((contact: Contact) => {
              const score = neglectScore(contact.last_contacted_at, contact.contact_frequency_days);
              const days = contact.last_contacted_at
                ? differenceInDays(new Date(), parseISO(contact.last_contacted_at))
                : null;
              return (
                <Link
                  key={contact.id}
                  href={`/contacts/${contact.id}`}
                  className="flex items-center justify-between hover:bg-gray-50 rounded px-1 py-0.5"
                >
                  <div className="flex items-center gap-2">
                    <span>{neglectEmoji(score)}</span>
                    <span className="text-sm">
                      {contact.first_name} {contact.last_name}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {days !== null ? `${days}d` : "never"}
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>

      {/* Due today */}
      {data.due_today.length > 0 && (
        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h2 className="font-semibold text-sm text-yellow-800 mb-2">Due Today</h2>
          <ul className="space-y-1">
            {data.due_today.map((r) => (
              <li key={r.id} className="text-sm text-yellow-900 flex items-center gap-2">
                <input type="checkbox" readOnly />
                {r.text}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
