"use client";
import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { getInteraction, pollAiSummary, toggleActionPoint } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { Interaction, AISummary, ActionPoint } from "@/lib/types";
import { sentimentColor, interactionTypeIcon, timeAgo } from "@/lib/utils";

export default function InteractionDetailPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  const [token, setToken] = useState("");
  const [interaction, setInteraction] = useState<Interaction | null>(null);
  const [summary, setSummary] = useState<AISummary | null>(null);
  const [loading, setLoading] = useState(true);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    getToken().then((t) => {
      if (!t) { router.push("/login"); return; }
      setToken(t);
      loadData(t);
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function loadData(t: string) {
    const data: any = await getInteraction(id, t);
    setInteraction(data.interaction);
    setSummary(data.ai_summary);
    setLoading(false);

    if (data.interaction.ai_status === "pending" || data.interaction.ai_status === "processing") {
      startPolling(t);
    }
  }

  function startPolling(t: string) {
    if (pollRef.current) return;
    let attempts = 0;
    pollRef.current = setInterval(async () => {
      attempts++;
      const result: any = await pollAiSummary(id, t).catch(() => null);
      if (!result) return;
      if (result.status === "done") {
        setSummary(result.summary);
        setInteraction((prev) => prev ? { ...prev, ai_status: "done" } : prev);
        clearInterval(pollRef.current!);
        pollRef.current = null;
      } else if (result.status === "failed" || attempts > 20) {
        setInteraction((prev) => prev ? { ...prev, ai_status: result.status } : prev);
        clearInterval(pollRef.current!);
        pollRef.current = null;
      }
    }, 3000);
  }

  useEffect(() => () => { if (pollRef.current) clearInterval(pollRef.current); }, []);

  async function handleToggleAP(index: number, current: boolean) {
    await toggleActionPoint(id, index, !current, token);
    setSummary((prev) => {
      if (!prev?.action_points) return prev;
      const pts: ActionPoint[] = JSON.parse(prev.action_points);
      pts[index].completed = !current;
      return { ...prev, action_points: JSON.stringify(pts) };
    });
  }

  if (loading) return <div className="p-8 text-gray-500">Loading…</div>;
  if (!interaction) return <div className="p-8 text-red-600">Not found</div>;

  const actionPoints: ActionPoint[] = summary?.action_points ? JSON.parse(summary.action_points) : [];
  const keyTopics: string[] = summary?.key_topics ? JSON.parse(summary.key_topics) : [];

  return (
    <div className="p-6 max-w-4xl">
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => router.back()} className="text-sm text-gray-500 hover:text-gray-900">
          ← Back
        </button>
        <h1 className="text-xl font-semibold">
          {interactionTypeIcon(interaction.interaction_type)} Interaction
        </h1>
        <span className="text-sm text-gray-400">{timeAgo(interaction.interaction_date)}</span>
      </div>

      <div className="grid grid-cols-2 gap-6">
        {/* Raw content */}
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-medium text-sm text-gray-600 mb-3">Original notes</h2>
          <pre className="text-sm whitespace-pre-wrap font-mono text-gray-800 leading-relaxed">
            {interaction.raw_content}
          </pre>
        </div>

        {/* AI Summary */}
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-medium text-sm text-gray-600 mb-3">AI Summary</h2>

          {(interaction.ai_status === "pending" || interaction.ai_status === "processing") && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              Processing with Claude…
            </div>
          )}

          {interaction.ai_status === "failed" && (
            <p className="text-sm text-red-600">AI processing failed. You can reprocess from the interaction menu.</p>
          )}

          {interaction.ai_status === "done" && summary && (
            <div className="space-y-4">
              {summary.sentiment && (
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${sentimentColor(summary.sentiment)}`}>
                  {summary.sentiment}
                </span>
              )}

              {summary.summary && (
                <p className="text-sm text-gray-800 leading-relaxed">{summary.summary}</p>
              )}

              {keyTopics.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {keyTopics.map((t, i) => (
                    <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                      {t}
                    </span>
                  ))}
                </div>
              )}

              {summary.follow_up_date && (
                <p className="text-xs text-blue-700">
                  Suggested follow-up: <strong>{summary.follow_up_date}</strong>
                </p>
              )}

              {actionPoints.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-gray-600 mb-2 uppercase tracking-wide">Action Points</h3>
                  <ul className="space-y-2">
                    {actionPoints.map((ap, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <input
                          type="checkbox"
                          checked={ap.completed ?? false}
                          onChange={() => handleToggleAP(i, ap.completed ?? false)}
                          className="mt-0.5"
                        />
                        <div>
                          <span className={`text-sm ${ap.completed ? "line-through text-gray-400" : "text-gray-800"}`}>
                            {ap.text}
                          </span>
                          {ap.due_date && (
                            <span className="block text-xs text-gray-400">{ap.due_date}</span>
                          )}
                        </div>
                        <span
                          className={`ml-auto text-xs font-medium ${
                            ap.priority === "high" ? "text-red-600" : ap.priority === "medium" ? "text-yellow-600" : "text-gray-400"
                          }`}
                        >
                          {ap.priority}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
