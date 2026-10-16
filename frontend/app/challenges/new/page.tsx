"use client";
import { ChallengeEditor } from "@/components/ChallengeEditor";
import { Section } from "@/components/OpportunityUI";
import { useAuth } from "@/lib/auth-context";
export default function NewChallengePage() {
  const { user } = useAuth();
  if (user?.role !== "business_owner") return <p>Only business owners can create challenges.</p>;
  return <div className="space-y-6"><h1 className="text-3xl font-semibold">Create a challenge</h1><p>Start with a business need or adapt a saved idea. Saving keeps the challenge private as a draft.</p><Section title="Challenge draft"><ChallengeEditor /></Section></div>;
}
