/* Controlled browser regression: delayed assessment responses are simulated,
   while login, plan creation and editing use the actual local application. */
const { chromium } = require(process.env.NASHAA_PLAYWRIGHT_MODULE || "playwright");
const assert = require("node:assert/strict");
const fs = require("node:fs/promises"), path = require("node:path");
const base = process.env.NASHAA_E2E_BASE || "http://localhost:3000";
const output = process.env.NASHAA_E2E_OUTPUT || path.join(process.cwd(), "e2e-results", "assessment-loading");
const results = []; let browser;
async function api(route, body, token) {
  const res = await fetch(base + "/api" + route, {method:"POST", headers:{"Content-Type":"application/json", ...(token ? {Authorization:"Bearer " + token} : {})}, body:JSON.stringify(body)});
  assert(res.ok, `HTTP ${res.status} ${route}`); return res.json();
}
function pass(name) { results.push({check:name,pass:true}); console.log("PASS " + name); }
(async () => {
  await fs.mkdir(output,{recursive:true});
  browser = await chromium.launch({channel:"chrome", headless:true});
  const context = await browser.newContext({viewport:{width:1366,height:900}});
  const page = await context.newPage(); page.setDefaultTimeout(30000);
  const runtimeErrors=[]; page.on("pageerror",e=>runtimeErrors.push(e.message));
  const email=`assessment-loading-${Date.now()}@example.com`, password="Password123!";
  const user=await api("/auth/register",{email,password,role:"business_owner",display_name:"Fictional Loading Test"});
  const idea=await api("/ideas",{name:"Fictional Loading Test Plan",problem:"Reusable cups are not returned.",solution:"Campus cup return pilot.",industry:"other",business_stage:"idea",target_location:"Fictional campus",intended_customers:"Campus cafes",budget:"Not supplied",current_challenges:"Return rates unknown",visibility:"private"},user.token);
  await page.addInitScript(token=>localStorage.setItem("nashaa_token",token),user.token);
  let state={current_status:"none",latest_attempt_status:null,latest_valid:null,in_progress:false,error_message:null};
  let finish, calls=0;
  await page.route(`**/api/ideas/${idea.id}/assessment`, async route=>{
    if(route.request().method()==="POST") { calls++; await new Promise(resolve=>{finish=resolve;}); }
    await route.fulfill({status:200,json:state});
  });
  const result={id:"11111111-1111-4111-8111-111111111111",idea_id:idea.id,idea_revision:1,provider:"mock",generation_status:"succeeded",input_snapshot:{},created_at:new Date().toISOString(),updated_at:new Date().toISOString(),error_message:null,market_considerations:"Fictional campus cup pilot review.",target_customer_analysis:"Campus cafes are the proposed customers.",competitor_considerations:"No competitor evidence supplied.",indicative_costs:"Washing costs remain unknown.",suggested_next_steps:"Measure cup returns at the pilot cafes.",assumptions:"Demand is unvalidated.",sources:"Simulated browser test response; no Gemini call."};
  function success() { state={current_status:"succeeded",latest_attempt_status:"succeeded",latest_valid:result,in_progress:false,error_message:null}; }
  const loading=()=>page.getByText("Your assessment is being generated",{exact:true});
  await page.goto(`${base}/ideas/${idea.id}`);
  await page.getByRole("button",{name:"Generate assessment",exact:true}).click();
  await loading().waitFor();
  const button=page.getByRole("button",{name:/Generating/}); assert(await button.isDisabled());
  await button.evaluate(el=>{el.click();el.click();}); assert.equal(calls,1);
  assert.equal(await page.getByText("No assessment yet",{exact:true}).count(),0);
  await page.waitForFunction(()=>document.querySelector('.assessment-sweep') && getComputedStyle(document.querySelector('.assessment-sweep')).animationName==='assessment-sweep');
  await page.getByText("The review considers your business model and customers.",{exact:true}).waitFor();
  const ticks=await page.evaluate(()=>new Promise(resolve=>{let ticks=0; const frame=()=>{if(++ticks===5)resolve(ticks);else requestAnimationFrame(frame);};requestAnimationFrame(frame);}));
  assert.equal(ticks,5); assert(await page.getByRole("link",{name:/Back$/}).isEnabled());
  await page.locator('.assessment-loading').screenshot({path:path.join(output,"loading-desktop.png")});
  pass("Immediate animated feedback, changing truthful messages, responsive rendering and duplicate prevention");
  success(); finish(); await page.locator(".assessment-result").getByText(result.market_considerations,{exact:true}).waitFor();
  assert.equal(await loading().count(),0); pass("Delayed success replaces loading with results");
  await page.getByRole("button",{name:"Regenerate assessment",exact:true}).click(); await loading().waitFor();
  await page.getByText("Your previous assessment remains available while the new one is generated.",{exact:true}).waitFor();
  state={...state,current_status:"failed",latest_attempt_status:"failed",error_message:"The AI assessment service took too long to respond. Please try again. Any previous successful assessment remains saved."};
  finish(); await page.getByRole("button",{name:"Retry assessment",exact:true}).waitFor();
  await page.getByRole("alert").filter({hasText:"took too long"}).waitFor(); assert.equal(await loading().count(),0);
  await page.locator(".assessment-result").getByText(result.market_considerations,{exact:true}).waitFor(); pass("Timeout stops animation, preserves previous result and offers retry");
  await page.unroute(`**/api/ideas/${idea.id}/assessment`);
  await page.route(`**/api/ideas/${idea.id}/assessment`,route=>route.request().method()==="POST" ? route.fulfill({status:503,json:{detail:"Assessment service temporarily unavailable. Please retry."}}) : route.fulfill({status:200,json:state}));
  await page.getByRole("button",{name:"Retry assessment",exact:true}).click();
  await page.getByText("Assessment service temporarily unavailable. Please retry.",{exact:true}).waitFor(); assert.equal(await loading().count(),0);
  assert(await page.getByRole("button",{name:"Retry assessment",exact:true}).isEnabled()); pass("HTTP failure clears loading and leaves retry available");
  await page.unroute(`**/api/ideas/${idea.id}/assessment`);
  await page.route(`**/api/ideas/${idea.id}/assessment`,async route=>{if(route.request().method()==="POST"){calls++;await new Promise(resolve=>{finish=resolve;});}await route.fulfill({status:200,json:state});});
  await page.getByRole("button",{name:"Retry assessment",exact:true}).click(); await loading().waitFor(); success(); finish();
  await page.getByRole("button",{name:"Regenerate assessment",exact:true}).waitFor(); pass("Retry succeeds without refreshing the page");
  state={...state,current_status:"in_progress",latest_attempt_status:"in_progress",in_progress:true};
  await page.reload(); await loading().waitFor(); assert(await page.getByRole("button",{name:/Generating/}).isDisabled());
  success(); await page.getByRole("button",{name:"Regenerate assessment",exact:true}).waitFor(); assert.equal(await loading().count(),0); pass("Existing server-side generation resumes loading and polling completes");
  await page.getByRole("button",{name:"Edit idea",exact:true}).click();
  await page.getByLabel("Idea name",{exact:true}).fill("Fictional Loading Test Plan Updated");
  await page.getByRole("button",{name:"Save and assess",exact:true}).click(); await loading().waitFor();
  result.id="22222222-2222-4222-8222-222222222222"; result.idea_revision=2; success(); finish();
  await page.getByRole("button",{name:"Regenerate assessment",exact:true}).waitFor(); pass("Save and assess uses the same loading and completion experience");
  await page.setViewportSize({width:390,height:844}); await page.emulateMedia({reducedMotion:"reduce"});
  await page.getByRole("button",{name:"Regenerate assessment",exact:true}).click(); await loading().waitFor();
  assert.equal(await page.locator('.assessment-sweep').evaluate(el=>getComputedStyle(el).animationName),'none');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('.assessment-loading').screenshot({path:path.join(output,"loading-mobile-reduced-motion.png")});
  success(); finish(); await page.getByRole("button",{name:"Regenerate assessment",exact:true}).waitFor(); pass("Mobile layout and reduced-motion preference work correctly");
  assert.deepEqual(runtimeErrors,[]); pass("No browser runtime errors");
})().catch(error=>{console.error(error);results.push({check:"Browser regression",pass:false,detail:error.message});process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();await fs.mkdir(output,{recursive:true});await fs.writeFile(path.join(output,"results.json"),JSON.stringify({date:new Date().toISOString(),simulatedAssessmentResponses:true,results},null,2));});
