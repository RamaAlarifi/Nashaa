"use client";
import { ActionForm } from "./OpportunityUI";
import { api } from "@/lib/api";
export function ReportContent({kind,id}:{kind:string;id:string}) {
  return <details className="rounded-xl border border-navy/10 p-4 text-sm"><summary className="cursor-pointer font-medium">Report this {kind}</summary><div className="mt-4"><ActionForm label="Submit report" resetOnSuccess fields={[{name:"category",label:"Report category",options:["spam","abuse","inappropriate_content","privacy","technical","other"].map(value=>({value,label:value.replaceAll("_"," ")}))},{name:"description",label:"Describe the issue",type:"textarea",maxLength:4000}]} submit={v=>api.opportunity("/reports","POST",{...v,target_type:kind,target_id:id})} /></div></details>;
}
