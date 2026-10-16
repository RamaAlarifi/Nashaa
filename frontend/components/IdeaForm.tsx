"use client";

import { Input, Select, TextArea } from "@/components/Input";
import { IndustrySelect } from "@/components/IndustrySelect";
import type { BusinessIdea, BusinessStage, IdeaVisibility } from "@/lib/types";
import { STAGE_LABELS, VISIBILITY_LABELS } from "@/lib/types";

export interface IdeaFormValues {
  industry_detail: string;
  business_model: string;
  value_proposition: string;
  revenue_model: string;
  market_opportunity: string;
  competition: string;
  cost_structure: string;
  growth_strategy: string;
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
  industry_detail: "", business_model: "", value_proposition: "", revenue_model: "",
  market_opportunity: "", competition: "", cost_structure: "", growth_strategy: "",
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
    industry_detail: idea.industry_detail ?? "", business_model: idea.business_model ?? "",
    value_proposition: idea.value_proposition ?? "", revenue_model: idea.revenue_model ?? "",
    market_opportunity: idea.market_opportunity ?? "", competition: idea.competition ?? "",
    cost_structure: idea.cost_structure ?? "", growth_strategy: idea.growth_strategy ?? "",
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
        <IndustrySelect
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
      <Input label="Industry specialisation (optional)" name="industry_detail" maxLength={240} value={values.industry_detail} error={errors.industry_detail} hint="For example, reusable packaging for restaurants." onChange={e => onChange("industry_detail", e.target.value)} />
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
      <details className="rounded-xl border border-navy/15 p-5" open>
        <summary className="cursor-pointer font-semibold">Business model and plan details (optional)</summary>
        <p className="my-4 text-sm text-muted-light">Add what you know. Leave unknown details empty so the assessment can identify gaps rather than assume facts. Label estimates and state the source of any market claims.</p>
        <div className="space-y-4">{([
          ["business_model", "Business model", "How the business operates, delivers its offer and serves customers."],
          ["value_proposition", "Value proposition", "Why these customers would choose this offer over alternatives."],
          ["revenue_model", "Revenue model", "Who pays, how pricing works and any assumptions about sales or recurring revenue."],
          ["market_opportunity", "Market opportunity and evidence", "Describe the opportunity and any observations, research or sources you actually have."],
          ["competition", "Competition and alternatives", "Known competitors, customer alternatives and your proposed difference."],
          ["cost_structure", "Costs and operating requirements", "Known setup and ongoing costs, suppliers, capacity and any financial estimates."],
          ["growth_strategy", "Growth strategy", "How you intend to attract, retain and serve more customers."],
        ] as const).map(([key, label, hint]) => <TextArea key={key} label={label} name={key} hint={hint} rows={3} maxLength={6000} value={values[key]} error={errors[key]} onChange={e => onChange(key, e.target.value)} />)}</div>
      </details>
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
