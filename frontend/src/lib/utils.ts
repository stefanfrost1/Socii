import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { formatDistanceToNow, differenceInDays, parseISO } from "date-fns";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function timeAgo(dateStr: string): string {
  return formatDistanceToNow(parseISO(dateStr), { addSuffix: true });
}

export function neglectScore(lastContactedAt?: string, frequencyDays?: number): number {
  if (!lastContactedAt) return 999;
  const days = differenceInDays(new Date(), parseISO(lastContactedAt));
  if (!frequencyDays) return days;
  return days / frequencyDays;
}

export function neglectColor(score: number): string {
  if (score > 2) return "text-red-600";
  if (score > 1) return "text-yellow-600";
  return "text-green-600";
}

export function neglectEmoji(score: number): string {
  if (score > 2) return "🔴";
  if (score > 1) return "🟡";
  return "🟢";
}

export function interactionTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    email: "📧",
    meeting: "🤝",
    call: "📞",
    sms: "💬",
    whatsapp: "💬",
    linkedin: "💼",
    other: "📝",
  };
  return icons[type] ?? "📝";
}

export function sentimentColor(sentiment?: string): string {
  if (sentiment === "positive") return "text-green-700 bg-green-50";
  if (sentiment === "negative") return "text-red-700 bg-red-50";
  return "text-gray-700 bg-gray-50";
}
