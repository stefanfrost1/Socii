"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { listReminders, updateReminder } from "@/lib/api";
import { getToken } from "@/lib/supabase";
import { Reminder } from "@/lib/types";
import { isToday, isBefore, parseISO } from "date-fns";

export default function RemindersPage() {
  const router = useRouter();
  const [token, setToken] = useState("");
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getToken().then((t) => {
      if (!t) { router.push("/login"); return; }
      setToken(t);
      listReminders({ completed: "false" }, t).then((data: any) => {
        setReminders(data);
        setLoading(false);
      });
    });
  }, [router]);

  async function complete(id: string) {
    await updateReminder(id, { is_completed: true }, token);
    setReminders((prev) => prev.filter((r) => r.id !== id));
  }

  const overdue = reminders.filter((r) => r.due_date && isBefore(parseISO(r.due_date), new Date()) && !isToday(parseISO(r.due_date)));
  const today = reminders.filter((r) => r.due_date && isToday(parseISO(r.due_date)));
  const upcoming = reminders.filter((r) => !r.due_date || (!isBefore(parseISO(r.due_date!), new Date()) && !isToday(parseISO(r.due_date!))));

  function Section({ title, items, color }: { title: string; items: Reminder[]; color: string }) {
    if (items.length === 0) return null;
    return (
      <div className="mb-6">
        <h2 className={`text-sm font-semibold mb-2 ${color}`}>{title}</h2>
        <div className="bg-white border rounded-lg divide-y">
          {items.map((r) => (
            <div key={r.id} className="flex items-start gap-3 px-4 py-3">
              <input
                type="checkbox"
                className="mt-0.5"
                onChange={() => complete(r.id)}
              />
              <div className="flex-1">
                <p className="text-sm">{r.text}</p>
                {r.due_date && <p className="text-xs text-gray-400 mt-0.5">{r.due_date}</p>}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-2xl">
      <h1 className="text-xl font-semibold mb-6">Reminders</h1>
      {loading ? (
        <p className="text-gray-500">Loading…</p>
      ) : (
        <>
          <Section title="Overdue" items={overdue} color="text-red-600" />
          <Section title="Today" items={today} color="text-yellow-700" />
          <Section title="Upcoming" items={upcoming} color="text-gray-700" />
          {reminders.length === 0 && <p className="text-sm text-gray-400">No pending reminders.</p>}
        </>
      )}
    </div>
  );
}
