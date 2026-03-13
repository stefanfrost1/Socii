export interface Contact {
  id: string;
  first_name: string;
  last_name?: string;
  display_name?: string;
  email?: string;
  phone?: string;
  title?: string;
  image_url?: string;
  linkedin_url?: string;
  twitter_url?: string;
  github_url?: string;
  instagram_url?: string;
  website_url?: string;
  address_city?: string;
  address_country?: string;
  bio_notes?: string;
  last_contacted_at?: string;
  contact_frequency_days?: number;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface Company {
  id: string;
  name: string;
  website_url?: string;
  linkedin_url?: string;
  industry?: string;
  size_range?: string;
  description?: string;
  logo_url?: string;
  address_city?: string;
  address_country?: string;
  is_archived: boolean;
}

export interface ProjectStage {
  id: string;
  name: string;
  order_index: number;
  color: string;
  is_terminal: boolean;
  is_default: boolean;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  stage_id?: string;
  stage_updated_at?: string;
  value_estimate?: number;
  currency: string;
  close_date_target?: string;
  outcome?: string;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
}

export interface ActionPoint {
  text: string;
  due_date?: string;
  priority: "high" | "medium" | "low";
  completed?: boolean;
  completed_at?: string;
}

export interface AISummary {
  id: string;
  interaction_id: string;
  summary?: string;
  action_points?: string; // JSON string
  follow_up_date?: string;
  key_topics?: string; // JSON string
  sentiment?: "positive" | "neutral" | "negative";
  model_used?: string;
  processed_at?: string;
}

export interface Interaction {
  id: string;
  contact_id: string;
  project_id?: string;
  raw_content: string;
  interaction_type: string;
  interaction_date: string;
  direction: string;
  from_whom?: string;
  ai_status: "pending" | "processing" | "done" | "failed";
  created_at: string;
}

export interface Reminder {
  id: string;
  contact_id?: string;
  project_id?: string;
  interaction_id?: string;
  text: string;
  due_date?: string;
  is_completed: boolean;
  completed_at?: string;
  created_at: string;
}

export interface Tag {
  id: string;
  name: string;
  color: string;
}

export interface MergeSuggestion {
  id: string;
  contact_a_id: string;
  contact_b_id: string;
  confidence_score: number;
  reasons?: string;
  status: "pending" | "accepted" | "rejected";
  created_at: string;
}

export interface DashboardOverview {
  recent_interactions: Array<{
    interaction: Interaction;
    ai_summary?: AISummary;
  }>;
  pipeline: Array<{ stage: ProjectStage; count: number }>;
  needs_contact: Contact[];
  due_today: Reminder[];
}
