"use client";
import { useRouter } from "next/navigation";
import { ActionForm, splitList, useResource } from "./OpportunityUI";
import { api } from "@/lib/api";
import type { BusinessIdea } from "@/lib/types";
import type { Challenge } from "@/lib/opportunity-types";

export function ChallengeEditor({ challenge, done }: { challenge?: Challenge; done?: () => Promise<void> }) {
  const router = useRouter(); const ideas = useResource<BusinessIdea[]>("/ideas");
  return <ActionForm key={challenge?.id ?? "new"} label="Save draft" fields={[
    { name: "idea_id", label: "Related idea", value: challenge?.idea_id ?? "", required: false, options: [{ value: "", label: "Independent business need" }, ...(ideas.data ?? []).map(i => ({ value: i.id, label: i.name }))] },
    { name: "title", label: "Challenge title", value: challenge?.title },
    { name: "problem", label: "Problem", type: "textarea", value: challenge?.problem, required: false },
    { name: "desired_outcome", label: "Desired outcome", type: "textarea", value: challenge?.desired_outcome, required: false },
    { name: "required_skills", label: "Required skills", value: challenge?.required_skills.join(", "), hint: "Separate skills with commas.", required: false },
    { name: "industry", label: "Industry", type: "industry", value: challenge?.industry, required: false },
    ...(["location", "timeline", "compensation"] as const).map(name => ({ name, label: name[0].toUpperCase() + name.slice(1), value: challenge?.[name], required: false, maxLength: name === "location" ? 120 : 200 })),
  ]} submit={async v => {
    const result = await api.opportunity<Challenge>(challenge ? `/challenges/${challenge.id}` : "/challenges", challenge ? "PUT" : "POST", { ...v, idea_id: v.idea_id || null, required_skills: splitList(v.required_skills) });
    if (done) await done(); else router.push(`/challenges/${result.id}`);
  }} />;
}
