"use client";
import { useEffect } from "react";
import { supabase } from "@/lib/supabase";

// Refresh the session at most once per 30 minutes of activity.
// Supabase will issue a new JWT each time, resetting the 7-day expiry window.
const REFRESH_INTERVAL_MS = 30 * 60 * 1000;
const STORAGE_KEY = "socii_last_session_refresh";

async function maybeRefresh() {
  const last = Number(localStorage.getItem(STORAGE_KEY) ?? 0);
  if (Date.now() - last < REFRESH_INTERVAL_MS) return;

  const { error } = await supabase.auth.refreshSession();
  if (!error) {
    localStorage.setItem(STORAGE_KEY, String(Date.now()));
  }
}

export function SessionRefresher() {
  useEffect(() => {
    // Refresh once on mount (page load counts as activity)
    maybeRefresh();

    const events = ["click", "keydown", "scroll", "pointerdown"] as const;
    const handler = () => maybeRefresh();
    events.forEach((e) => window.addEventListener(e, handler, { passive: true }));
    return () => events.forEach((e) => window.removeEventListener(e, handler));
  }, []);

  return null;
}
