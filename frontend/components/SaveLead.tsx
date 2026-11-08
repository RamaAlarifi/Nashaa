"use client";
import { useState } from "react";
import Link from "next/link";
import { Button } from "./Button";
import { api } from "@/lib/api";
export function SaveLead({ideaId,referenceId,kind}:{ideaId:string;referenceId:string;kind:"customer"|"investor"}) {
  const [busy,setBusy]=useState(false),[saved,setSaved]=useState(""),[error,setError]=useState("");
  return <div className="space-y-2"><Button variant="secondary" disabled={!!saved} loading={busy} onClick={async()=>{setBusy(true);setError("");try{const lead=await api.opportunity<{id:string}>(`/ideas/${ideaId}/leads`,"POST",{kind,reference_id:referenceId});setSaved(lead.id);}catch(e){setError(e instanceof Error?e.message:"Could not save lead.");}finally{setBusy(false);}}}>{saved?"Lead saved":"Save lead"}</Button>{saved&&<p role="status"><Link className="text-brand-700 underline" href={`/leads/${saved}`}>Open saved lead</Link></p>}{error&&<p role="alert" className="text-red-700">{error}</p>}</div>;
}
