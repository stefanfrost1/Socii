const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}/api/v1${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "API error");
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// Dashboard
export const getDashboardOverview = (token: string) =>
  request("/dashboard/overview", {}, token);

// Contacts
export const listContacts = (params: Record<string, string>, token: string) =>
  request(`/contacts?${new URLSearchParams(params)}`, {}, token);

export const getContact = (id: string, token: string) =>
  request(`/contacts/${id}`, {}, token);

export const createContact = (data: unknown, token: string) =>
  request("/contacts", { method: "POST", body: JSON.stringify(data) }, token);

export const updateContact = (id: string, data: unknown, token: string) =>
  request(`/contacts/${id}`, { method: "PATCH", body: JSON.stringify(data) }, token);

export const deleteContact = (id: string, token: string) =>
  request(`/contacts/${id}`, { method: "DELETE" }, token);

export const getContactTimeline = (id: string, token: string) =>
  request(`/contacts/${id}/timeline`, {}, token);

export const getNeedsContact = (token: string) =>
  request("/contacts/needs-contact", {}, token);

export const searchImageCandidates = (id: string, token: string) =>
  request(`/contacts/${id}/image/search`, { method: "POST" }, token);

export const importContactImage = (id: string, url: string, token: string) =>
  request(`/contacts/${id}/image/import`, { method: "POST", body: JSON.stringify({ url }) }, token);

// Companies
export const listCompanies = (params: Record<string, string>, token: string) =>
  request(`/companies?${new URLSearchParams(params)}`, {}, token);

export const getCompany = (id: string, token: string) =>
  request(`/companies/${id}`, {}, token);

export const createCompany = (data: unknown, token: string) =>
  request("/companies", { method: "POST", body: JSON.stringify(data) }, token);

export const updateCompany = (id: string, data: unknown, token: string) =>
  request(`/companies/${id}`, { method: "PATCH", body: JSON.stringify(data) }, token);

// Projects
export const listProjects = (params: Record<string, string>, token: string) =>
  request(`/projects?${new URLSearchParams(params)}`, {}, token);

export const getProject = (id: string, token: string) =>
  request(`/projects/${id}`, {}, token);

export const createProject = (data: unknown, token: string) =>
  request("/projects", { method: "POST", body: JSON.stringify(data) }, token);

export const updateProject = (id: string, data: unknown, token: string) =>
  request(`/projects/${id}`, { method: "PATCH", body: JSON.stringify(data) }, token);

// Interactions
export const createInteraction = (data: unknown, token: string) =>
  request("/interactions", { method: "POST", body: JSON.stringify(data) }, token);

export const getInteraction = (id: string, token: string) =>
  request(`/interactions/${id}`, {}, token);

export const pollAiSummary = (id: string, token: string) =>
  request(`/interactions/${id}/ai-summary`, {}, token);

export const toggleActionPoint = (interactionId: string, apIndex: number, completed: boolean, token: string) =>
  request(
    `/interactions/${interactionId}/action-points/${apIndex}`,
    { method: "PATCH", body: JSON.stringify({ completed }) },
    token
  );

// Stages
export const listStages = (token: string) =>
  request("/stages", {}, token);

export const updateStage = (id: string, data: unknown, token: string) =>
  request(`/stages/${id}`, { method: "PUT", body: JSON.stringify(data) }, token);

export const reorderStages = (order: { id: string; order_index: number }[], token: string) =>
  request("/stages/reorder", { method: "POST", body: JSON.stringify({ order }) }, token);

// Tags
export const listTags = (token: string) =>
  request("/tags", {}, token);

export const createTag = (data: { name: string; color?: string }, token: string) =>
  request("/tags", { method: "POST", body: JSON.stringify(data) }, token);

export const deleteTag = (id: string, token: string) =>
  request(`/tags/${id}`, { method: "DELETE" }, token);

// Reminders
export const listReminders = (params: Record<string, string>, token: string) =>
  request(`/reminders?${new URLSearchParams(params)}`, {}, token);

export const updateReminder = (id: string, data: unknown, token: string) =>
  request(`/reminders/${id}`, { method: "PATCH", body: JSON.stringify(data) }, token);

// Search
export const globalSearch = (q: string, token: string) =>
  request(`/search?q=${encodeURIComponent(q)}`, {}, token);

// Merge suggestions
export const listMergeSuggestions = (token: string) =>
  request("/contacts/merge-suggestions", {}, token);

export const triggerMergeScan = (token: string) =>
  request("/contacts/merge-suggestions/scan", { method: "POST" }, token);

export const resolvesuggestion = (id: string, status: string, token: string) =>
  request(`/contacts/merge-suggestions/${id}`, { method: "PATCH", body: JSON.stringify({ status }) }, token);

export const mergeContacts = (keepId: string, discardId: string, overrides: Record<string, unknown>, token: string) =>
  request("/contacts/merge", { method: "POST", body: JSON.stringify({ keep_id: keepId, discard_id: discardId, field_overrides: overrides }) }, token);
