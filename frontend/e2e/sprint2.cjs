/* Fictional demo journeys. Set NASHAA_PLAYWRIGHT_MODULE if Playwright is external. */
const { chromium } = require(process.env.NASHAA_PLAYWRIGHT_MODULE || "playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const base = process.env.NASHAA_E2E_BASE || "http://localhost:3000";
const output = process.env.NASHAA_E2E_OUTPUT || path.join(process.cwd(), "e2e-results");
const password = "Password123!", stamp = Date.now(), results = [];
let browser;
async function api(route, method="GET", body, token) {
  const r = await fetch(`${base}/api${route}`, {method, headers:{"Content-Type":"application/json", ...(token ? {Authorization:`Bearer ${token}`} : {})}, body:body === undefined ? undefined : JSON.stringify(body)});
  const data = r.status === 204 ? null : await r.json(); if (!r.ok) throw Error(`${method} ${route}: ${r.status} ${data.detail}`); return data;
}
async function login(email, loginPassword = password) {
  const context = await browser.newContext({viewport:{width:1366,height:900}}), page = await context.newPage();
  page.setDefaultTimeout(45000); page.on("dialog", d=>d.accept());
  page.on("pageerror", e=>results.push({check:"Browser runtime error",pass:false,detail:e.message}));
  await page.goto(`${base}/login`); await page.getByLabel("Email",{exact:true}).fill(email); await page.getByLabel("Password",{exact:true}).fill(loginPassword);
  await page.getByRole("button",{name:"Sign in",exact:true}).click(); await page.waitForURL("**/dashboard"); return page;
}
async function check(name, page, run) { await run(); await page.evaluate(()=>window.scrollTo(0,0)); await page.screenshot({path:path.join(output,`${results.length+1}.png`),fullPage:true}); results.push({check:name,pass:true}); console.log(`PASS ${name}`); }
const label=(p,name)=>p.getByLabel(name,{exact:true}), button=(p,name)=>p.getByRole("button",{name,exact:true});
(async()=>{
  await fs.mkdir(output,{recursive:true}); browser=await chromium.launch({channel:"chrome",headless:true});
  const users={}; for(const [name,role] of [["Owner","business_owner"],["Innovator","innovator"],["Investor","investor"]]) {
    const email=`s2-ui-${name.toLowerCase()}-${stamp}@example.com`;
    users[name]={...(await api("/auth/register","POST",{email,password,role,display_name:`Fictional UI ${name} ${stamp}`})),email};
  }
  const admin=await api("/auth/login","POST",{email:"admin@nashaa.sa",password:process.env.NASHAA_DEMO_ADMIN_PASSWORD||password});
  const owner=await login(users.Owner.email), innovator=await login(users.Innovator.email), investor=await login(users.Investor.email);
  const adminPage=await login("admin@nashaa.sa",process.env.NASHAA_DEMO_ADMIN_PASSWORD||password); let challengeId,ideaId;
  await check("Verification request and administrator review",adminPage,async()=>{
    await owner.goto(`${base}/verification`); await label(owner,"Professional or business information").fill("Fictional restaurant owner background for browser testing."); await button(owner,"Submit verification request").click(); await owner.getByRole("heading",{name:"Current status: pending"}).waitFor();
    await adminPage.goto(`${base}/verification`); const card=adminPage.getByRole("heading",{name:`Fictional UI Owner ${stamp} Â· pending`,exact:true}).locator(".."); await card.getByLabel("Decision reason").fill("Fictional browser test review approved."); await card.getByRole("button",{name:"Record decision"}).click(); await adminPage.getByRole("heading",{name:`Fictional UI Owner ${stamp} Â· approved`,exact:true}).waitFor();
    for(const name of ["Innovator","Investor"]) {const r=await api("/verification","POST",{information:"Fictional professional background for browser testing."},users[name].token); await api(`/admin/verification/${r.id}/decision`,"POST",{decision:"approved",reason:"Fictional review approved."},admin.token);}
  });
  await check("Challenge creation and explicit publication",owner,async()=>{
    await owner.goto(`${base}/challenges/new`); for(const [name,value] of Object.entries({"Challenge title":`Fictional UI challenge ${stamp}`,Problem:"Reduce waste in a fictional restaurant.","Desired outcome":"A reusable packaging prototype.","Required skills":"Design, Prototyping",Industry:"Packaging",Location:"Riyadh",Timeline:"4 weeks"})) { if(name==="Industry") await label(owner,name).selectOption("manufacturing_packaging"); else await label(owner,name).fill(value); }
    await button(owner,"Save draft").click(); await owner.waitForURL(/\/challenges\/[0-9a-f-]+$/); challengeId=owner.url().split("/").pop(); await button(owner,"Approve and publish").click(); await button(owner,"Approve and publish").waitFor({state:"hidden"});
  });
  await check("Challenge filtering and proposal submission",innovator,async()=>{
    await innovator.goto(`${base}/challenges`); await label(innovator,"Search").fill(`Fictional UI challenge ${stamp}`);
    await Promise.all([innovator.waitForResponse(r=>r.url().includes("/api/challenges?")&&r.url().includes("q=Fictional")&&r.ok()),button(innovator,"Apply filters").click()]);
    await innovator.waitForFunction(()=>document.querySelectorAll('a.text-brand-700[href^="/challenges/"]').length===1);
    await innovator.getByRole("link",{name:"Open challenge",exact:true}).click();
    for(const [name,value] of Object.entries({"Proposed approach":"Develop and test a reusable prototype.",Deliverables:"Design files, prototype and testing notes.","Expected timeline":"4 weeks","Proposed cost (SAR)":"5000"})) await label(innovator,name).fill(value);
    await button(innovator,"Submit proposal").click(); await innovator.getByRole("heading",{name:"Your proposal",exact:true}).waitFor();
  });
  await check("Proposal comparison and collaborator selection",owner,async()=>{await owner.goto(`${base}/challenges/${challengeId}`); await button(owner,"Select collaborator").click(); await button(owner,"Select collaborator").waitFor({state:"hidden"});});
  await check("Contact approval and text conversation",innovator,async()=>{
    await button(owner,"Request contact").click(); await innovator.goto(`${base}/messages`); await button(innovator,"Accept").click(); await innovator.getByRole("button",{name:new RegExp(`Fictional UI Owner ${stamp}.*Fictional UI challenge`)}).click();
    await label(innovator,"Message").fill("Ready for the first design review."); await button(innovator,"Send message").click(); await innovator.getByText("Ready for the first design review.",{exact:true}).waitFor();
  });
  await check("Investment preferences and history",investor,async()=>{
    await investor.goto(`${base}/investments`); for(const [name,value] of Object.entries({Industries:"Packaging","Business stages":"idea","Preferred locations":"Riyadh","Minimum investment (SAR)":"1000","Maximum investment (SAR)":"100000"})) { if(name==="Industries") await label(investor,name).selectOption(["manufacturing_packaging"]); else await label(investor,name).fill(value); } await button(investor,"Save preferences").click();
    await label(investor,"Project name").fill("Fictional previous project"); await label(investor,"Industry").selectOption("manufacturing_packaging"); await label(investor,"Source or provenance").fill("Fictional browser test data"); await button(investor,"Add history entry").click(); await investor.getByText("Source: Fictional browser test data",{exact:true}).waitFor();
  });
  await check("Owner funding, investor suggestions and assessment approval",owner,async()=>{
    const idea=await api("/ideas","POST",{name:`Fictional UI idea ${stamp}`,industry:"Packaging",problem:"Reduce packaging waste",solution:"Reuse packaging",target_location:"Riyadh",visibility:"registered"},users.Owner.token); ideaId=idea.id;
    await owner.goto(`${base}/ideas/${ideaId}`); await button(owner,"Generate assessment").click(); await owner.getByText("Preview the assessment the investor will receive",{exact:true}).waitFor(); await label(owner,"Funding required (SAR)").fill("5000"); await button(owner,"Save funding requirement").click();
    await label(owner,"Investor").selectOption({label:`Fictional UI Investor ${stamp}`}); await button(owner,"Approve this assessment for the selected investor").click(); await button(owner,"Revoke access").waitFor();
  });
  await check("Approved investor assessment view",investor,async()=>{await investor.goto(`${base}/investments`); await investor.getByRole("link",{name:new RegExp(`Fictional UI idea ${stamp} Â· assessment revision`)}).click(); await investor.getByRole("heading",{name:"Market considerations",exact:true}).waitFor(); assert(!await investor.getByText("input_snapshot",{exact:true}).count());});
  await check("Save and Assess preserves an earlier shared version",owner,async()=>{
    const before = await api("/assessment-shares","GET",undefined,users.Investor.token);
    await button(owner,"Edit idea").click(); await label(owner,"Problem being solved").fill("Updated fictional packaging problem for the second revision."); await button(owner,"Save and assess").click();
    await owner.getByText("Assessment revision 2",{exact:true}).waitFor();
    const after = await api("/assessment-shares","GET",undefined,users.Investor.token);
    assert.equal(after[0].assessment.id,before[0].assessment.id);
    assert.equal(after[0].stale,true);
    await label(owner,"Assessment version to share").selectOption(before[0].assessment.id);
    await owner.getByText("Assessment revision 1",{exact:true}).waitFor();
  });
  await check("Assessment access revoked immediately",investor,async()=>{await button(owner,"Revoke access").click(); await button(owner,"Revoke access").waitFor({state:"hidden"}); await investor.reload(); await investor.getByRole("alert").filter({hasText:"unavailable"}).waitFor();});
  await check("Phone navigation and keyboard focus",innovator,async()=>{await innovator.setViewportSize({width:390,height:844}); await innovator.goto(`${base}/challenges`); await button(innovator,"Toggle navigation menu").click(); await innovator.getByRole("link",{name:"My proposals",exact:true}).click(); await innovator.getByRole("heading",{name:"My proposals",exact:true}).waitFor(); assert(await innovator.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)); await innovator.keyboard.press("Tab"); assert(await innovator.evaluate(()=>document.activeElement!==document.body));});
  assert(results.every(r=>r.pass),"Browser runtime errors occurred.");
})().catch(e=>{results.push({check:"Browser journey",pass:false,detail:e.message});console.error(e.message);process.exitCode=1;}).finally(async()=>{await fs.mkdir(output,{recursive:true});await fs.writeFile(path.join(output,"results.json"),JSON.stringify({date:new Date().toISOString(),results},null,2));if(browser)await browser.close();});
