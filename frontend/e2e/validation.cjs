/* Negative and boundary checks for the shared Sprint 2 form feedback. */
const {chromium}=require(process.env.NASHAA_PLAYWRIGHT_MODULE||"playwright");
const fs=require("node:fs/promises"),path=require("node:path"),assert=require("node:assert/strict");
const base=process.env.NASHAA_E2E_BASE||"http://localhost:3000", output=process.env.NASHAA_E2E_OUTPUT||path.join(process.cwd(),"e2e-results");
let browser;
(async()=>{
 const email=`s2-validation-${Date.now()}@example.com`,password="Password123!";
 const registration=await fetch(base+"/api/auth/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email,password,role:"investor",display_name:"Fictional validation investor"})});assert.equal(registration.status,201);const auth=await registration.json();
 browser=await chromium.launch({channel:"chrome",headless:true});const page=await browser.newPage({viewport:{width:1366,height:900}});page.setDefaultTimeout(45000);
 await page.goto(base+"/login");await page.getByLabel("Email",{exact:true}).fill(email);await page.getByLabel("Password",{exact:true}).fill(password);await page.getByRole("button",{name:"Sign in",exact:true}).click();await page.waitForURL("**/dashboard");await page.goto(base+"/investments");
 await page.getByLabel("Industries",{exact:true}).selectOption(["manufacturing_packaging"]);await page.getByLabel("Business stages",{exact:true}).fill("unknown");await page.getByLabel("Minimum investment (SAR)").fill("1");await page.getByLabel("Maximum investment (SAR)").fill("100");
 await page.getByRole("button",{name:"Save preferences",exact:true}).click();await page.locator('[name="stages"][aria-invalid="true"]').waitFor();
 await page.getByLabel("Business stages",{exact:true}).fill("idea");await page.getByLabel("Minimum investment (SAR)").fill("200");await page.getByRole("button",{name:"Save preferences",exact:true}).click();await page.getByRole("alert").filter({hasText:"Maximum funding must be at least the minimum"}).waitFor();
 await fs.mkdir(output,{recursive:true});await page.screenshot({path:path.join(output,"validation-error.png"),fullPage:true});
 await page.getByLabel("Minimum investment (SAR)").fill("0");await Promise.all([page.waitForResponse(r=>r.url().endsWith("/api/investor-preferences")&&r.request().method()==="PUT"&&r.status()===200),page.getByRole("button",{name:"Save preferences",exact:true}).click()]);
 const saved=await(await fetch(base+"/api/investor-preferences",{headers:{Authorization:"Bearer "+auth.token}})).json();assert.equal(saved.min_funding,"0.00");
 await fs.writeFile(path.join(output,"validation-results.json"),JSON.stringify({checks:["Invalid stage highlights the correct field","Invalid funding range displays the specific reason","Zero funding boundary saves as an exact decimal string"],passed:3},null,2));console.log("3 validation and boundary browser checks passed");
})().catch(e=>{console.error(e.message);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close()});
