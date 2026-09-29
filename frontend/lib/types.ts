// Shared types matching the backend Pydantic schemas.

export type Role = "business_owner" | "innovator" | "investor" | "admin";
export type AccountStatus = "active" | "suspended" | "deactivated";
export type BusinessStage =
  "idea" | "validation" | "early" | "operating" | "scaling";
export type IdeaVisibility = "private" | "registered";
export type ProfileVisibility = "public" | "registered" | "private";
export type AssessmentStatus =
  "pending" | "in_progress" | "succeeded" | "failed";

export interface User {
  id: string;
  email: string;
  role: Role;
  account_status: AccountStatus;
  created_at: string;
  updated_at: string;
}

export interface Profile {
  user_id: string;
  display_name: string;
  location: string;
  short_description: string;
  role_specific_info: Record<string, unknown>;
  profile_visibility: ProfileVisibility;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  token: string;
  token_type: string;
  user: User;
  profile: Profile | null;
}

export interface MeResponse {
  user: User;
  profile: Profile | null;
}

export interface BusinessIdea {
  id: string;
  owner_id: string;
  name: string;
  problem: string;
  solution: string;
  industry: string;
  business_stage: BusinessStage;
  target_location: string;
  intended_customers: string;
  budget: string;
  current_challenges: string;
  visibility: IdeaVisibility;
  revision_number: number;
  created_at: string;
  updated_at: string;
}

// Reduced view returned to non-owners under "registered" visibility.
export interface BusinessIdeaSummary {
  id: string;
  owner_id: string;
  name: string;
  industry: string;
  business_stage: BusinessStage;
  target_location: string;
  intended_customers: string;
  visibility: IdeaVisibility;
  revision_number: number;
}

export interface Assessment {
  id: string;
  idea_id: string;
  idea_revision: number;
  input_snapshot: Record<string, unknown>;
  generation_status: AssessmentStatus;
  error_message: string | null;
  created_at: string;
  updated_at: string;
  market_considerations: string;
  target_customer_analysis: string;
  competitor_considerations: string;
  indicative_costs: string;
  suggested_next_steps: string;
  assumptions: string;
  sources: string;
}

export interface AssessmentStatusResponse {
  current_status: string; // "none" | AssessmentStatus
  latest_attempt_status: AssessmentStatus | null;
  latest_valid: Assessment | null;
  in_progress: boolean;
  error_message: string | null;
}

export interface DashboardIdeaItem {
  id: string;
  name: string;
  industry: string;
  business_stage: string;
  visibility: string;
  revision_number: number;
  assessment_status: string; // "none" | AssessmentStatus
}

export interface Dashboard {
  role: Role;
  display_name: string;
  ideas: DashboardIdeaItem[] | null;
  message: string | null;
}

// Friendly human-readable labels for enums (used across screens).
export const ROLE_LABELS: Record<Role, string> = {
  business_owner: "Business owner",
  innovator: "Innovator",
  investor: "Investor",
  admin: "Administrator",
};

export const STAGE_LABELS: Record<BusinessStage, string> = {
  idea: "Idea",
  validation: "Validation",
  early: "Early stage",
  operating: "Operating",
  scaling: "Scaling",
};

export const VISIBILITY_LABELS: Record<IdeaVisibility, string> = {
  private: "Private (only me)",
  registered: "Registered users (summary only)",
};
