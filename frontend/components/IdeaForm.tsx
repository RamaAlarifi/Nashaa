"use client";

import { Input, Select, TextArea } from "@/components/Input";
import type { BusinessIdea, BusinessStage, IdeaVisibility } from "@/lib/types";
import { STAGE_LABELS, VISIBILITY_LABELS } from "@/lib/types";

export interface IdeaFormValues {
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
}

export const EMPTY_IDEA: IdeaFormValues = {
  name: "",
  problem: "",
  solution: "",
  industry: "",
  business_stage: "idea",
  target_location: "",
  intended_customers: "",
  budget: "",
  current_challenges: "",
  visibility: "private",
};

export function ideaToForm(idea: BusinessIdea): IdeaFormValues {
  return {
    name: idea.name,
    problem: idea.problem,
    solution: idea.solution,
    industry: idea.industry,
    business_stage: idea.business_stage,
    target_location: idea.target_location,
    intended_customers: idea.intended_customers,
    budget: idea.budget,
    current_challenges: idea.current_challenges,
    visibility: idea.visibility,
  };
}

interface Props {
  values: IdeaFormValues;
  errors: Record<string, string>;
  onChange: <K extends keyof IdeaFormValues>(
    key: K,
    value: IdeaFormValues[K],
  ) => void;
}

export function IdeaForm({ values, errors, onChange }: Props) {
  return (
    <div className="space-y-5">
      <div className="border-b border-navy/10 pb-4">
        <p className="eyebrow text-brand-700">01 / The foundation</p>
        <h2 className="mt-2 text-lg font-semibold">
          What do you have in mind?
        </h2>
        <p className="mt-1 text-sm text-muted-light">
          Start with the problem and how you want to solve it.
        </p>
      </div>
      <Input
        label="Idea name"
        name="name"
        required
        value={values.name}
        error={errors.name}
        onChange={(e) => onChange("name", e.target.value)}
      />
      <TextArea
        label="Problem being solved"
        name="problem"
        rows={3}
        hint="The customer pain or need your idea addresses."
        value={values.problem}
        error={errors.problem}
        onChange={(e) => onChange("problem", e.target.value)}
      />
      <TextArea
        label="Proposed solution"
        name="solution"
        rows={3}
        value={values.solution}
        error={errors.solution}
        onChange={(e) => onChange("solution", e.target.value)}
      />
      <div className="border-b border-navy/10 pb-4 pt-4">
        <p className="eyebrow text-brand-700">02 / The context</p>
        <h2 className="mt-2 text-lg font-semibold">
          Put your idea in perspective.
        </h2>
        <p className="mt-1 text-sm text-muted-light">
          These details help make your assessment more useful.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <Input
          label="Industry"
          name="industry"
          value={values.industry}
          error={errors.industry}
          onChange={(e) => onChange("industry", e.target.value)}
        />
        <Select
          label="Business stage"
          name="business_stage"
          value={values.business_stage}
          onChange={(e) =>
            onChange("business_stage", e.target.value as BusinessStage)
          }
        >
          {(Object.keys(STAGE_LABELS) as BusinessStage[]).map((s) => (
            <option key={s} value={s}>
              {STAGE_LABELS[s]}
            </option>
          ))}
        </Select>
      </div>
      <div className="grid gap-4 sm:grid-cols-2">
        <Input
          label="Target location"
          name="target_location"
          value={values.target_location}
          error={errors.target_location}
          onChange={(e) => onChange("target_location", e.target.value)}
        />
        <Input
          label="Available budget / cost range"
          name="budget"
          value={values.budget}
          error={errors.budget}
          onChange={(e) => onChange("budget", e.target.value)}
        />
      </div>
      <TextArea
        label="Intended customers"
        name="intended_customers"
        rows={2}
        value={values.intended_customers}
        error={errors.intended_customers}
        onChange={(e) => onChange("intended_customers", e.target.value)}
      />
      <TextArea
        label="Current challenges"
        name="current_challenges"
        rows={2}
        value={values.current_challenges}
        error={errors.current_challenges}
        onChange={(e) => onChange("current_challenges", e.target.value)}
      />
      <div className="border-b border-navy/10 pb-4 pt-4">
        <p className="eyebrow text-brand-700">03 / Your choice</p>
        <h2 className="mt-2 text-lg font-semibold">Choose who can see it.</h2>
        <p className="mt-1 text-sm text-muted-light">
          Keep it private, or share a limited summary with registered users.
        </p>
      </div>
      <Select
        label="Visibility"
        name="visibility"
        value={values.visibility}
        onChange={(e) =>
          onChange("visibility", e.target.value as IdeaVisibility)
        }
      >
        {(Object.keys(VISIBILITY_LABELS) as IdeaVisibility[]).map((v) => (
          <option key={v} value={v}>
            {VISIBILITY_LABELS[v]}
          </option>
        ))}
      </Select>
    </div>
  );
}
