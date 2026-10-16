import type { BusinessIdeaSummary, BusinessStage } from "./types";

export interface Challenge {
  id: string; owner_id: string; idea_id: string | null; title: string;
  problem: string; desired_outcome: string; required_skills: string[];
  industry: string; location: string; timeline: string; compensation: string;
  status: "draft" | "published" | "closed";
}
export interface Proposal {
  id: string; challenge_id: string; innovator_id: string; approach: string;
  deliverables: string; timeline: string; cost: string | null;
  status: string; innovator_name?: string; challenge_title?: string;
}
export interface Verification {
  id: string; user_id: string; information: string; reference: string;
  status: string; decision_reason: string; applicant_name?: string;
}
export interface Contact {
  id: string; sender_id: string; recipient_id: string; status: string;
  idea_id: string | null; challenge_id: string | null;
  participant_name: string; context_title: string;
}
export interface Conversation {
  id: string; participant_name: string; context_title: string;
}
export interface Message {
  id: string; sender_id: string; body: string; created_at: string;
}
export interface Preference {
  industries: string[]; stages: BusinessStage[]; locations: string[];
  min_funding: string; max_funding: string;
}
export interface History {
  id: string; project_name: string; industry: string; stage: BusinessStage; source: string;
}
export interface Match {
  idea: BusinessIdeaSummary; investor_id: string; investor_name: string;
  score: number; coverage: number; reasons: string[]; mismatches: string[];
  missing: string[]; history_sources: string[];
}
export interface Share {
  id: string; assessment_id: string; investor_id: string; investor_name: string;
  revoked_at: string | null;
}
export interface SharedAssessment {
  share_id: string; idea: BusinessIdeaSummary; stale: boolean;
  assessment: {
    provider: "mock" | "gemini" | "unknown";
    id: string; idea_revision: number; created_at: string;
    market_considerations: string; target_customer_analysis: string;
    competitor_considerations: string; indicative_costs: string;
    suggested_next_steps: string; assumptions: string; sources: string;
  };
}
