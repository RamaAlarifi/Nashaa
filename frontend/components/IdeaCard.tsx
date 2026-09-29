import Link from "next/link";
import { Badge } from "./Badge";
import { Icon } from "./Icon";
import {
  STAGE_LABELS,
  VISIBILITY_LABELS,
  type BusinessStage,
  type IdeaVisibility,
} from "@/lib/types";

const STATUS = {
  none: { tone: "neutral", text: "Ready to assess" },
  pending: { tone: "info", text: "Assessment queued" },
  in_progress: { tone: "info", text: "Generating assessment" },
  succeeded: { tone: "success", text: "Assessment ready" },
  failed: { tone: "danger", text: "Assessment needs attention" },
} as const;

export function IdeaCard({
  idea,
}: {
  idea: {
    id: string;
    name: string;
    industry: string;
    business_stage: string;
    revision_number: number;
    visibility: string;
    assessment_status?: string;
  };
}) {
  const status = idea.assessment_status
    ? (STATUS[idea.assessment_status as keyof typeof STATUS] ?? STATUS.none)
    : null;
  return (
    <Link href={`/ideas/${idea.id}`} className="idea-card group">
      <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-brand-50 text-brand-700">
        <Icon name="idea" />
      </span>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium text-muted-light">
          {idea.industry || "Industry not set"}
        </p>
        <h3 className="mt-1 break-words text-lg font-semibold group-hover:text-brand-700">
          {idea.name}
        </h3>
        <p className="mt-2 text-xs text-muted-light">
          {STAGE_LABELS[idea.business_stage as BusinessStage] ??
            idea.business_stage}
          <span className="mx-2" aria-hidden="true">
            ·
          </span>
          Revision {idea.revision_number}
        </p>
      </div>
      <div className="flex items-center gap-4 self-start sm:self-center">
        {status ? (
          <Badge tone={status.tone}>{status.text}</Badge>
        ) : (
          <Badge>
            {VISIBILITY_LABELS[idea.visibility as IdeaVisibility] ??
              idea.visibility}
          </Badge>
        )}
        <Icon name="arrow" className="h-4 w-4 shrink-0 text-brand-700" />
      </div>
    </Link>
  );
}
