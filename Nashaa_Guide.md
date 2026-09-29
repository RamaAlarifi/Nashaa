# Nashaa Complete Project Guide

## Purpose of this document

This document gives another AI model enough context to understand, plan, build, test, and document the Nashaa senior project without needing to read the original WhatsApp chat or every attached file.

Use this document as the main project guide. Do not treat old project examples, rejected ideas, casual chat suggestions, or unapproved feature ideas as requirements.

The project must be delivered in **three sprints**. Each sprint must produce working software, tests, documentation, a demonstration, a review, and a record of each student's contribution.

## 1. Project summary

### Project name

**Nashaa AI Platform for Saudi SMEs**

### Product type

A responsive web platform. It is not a native mobile application.

### Main purpose

Nashaa helps entrepreneurs and small-business owners in Saudi Arabia move from a business idea to practical action.

The platform should help a business owner:

1. Describe and assess a business idea.
2. Understand possible customers, competitors, costs, assumptions, and next steps.
3. Publish a business problem that an innovator can solve.
4. Compare proposals and choose a collaborator.
5. Find investors whose interests fit the business.
6. Define target customers and track possible customer or investor leads.

The platform also gives innovators, investors, and administrators their own accounts and tasks.

### Central project idea

The important value is not any one feature by itself. The value is keeping business planning, collaboration, investor discovery, and customer discovery connected to the same business idea and workspace.

## 2. Why the project was selected

The team discussed many other ideas, including smart parking, healthcare recovery, cybersecurity reporting, emergency assistance, lost-and-found matching, document scanning, and drone-based vehicle detection.

Those ideas were rejected, considered too difficult, or abandoned. They are not part of Nashaa.

Nashaa was selected because:

- It addresses a real problem faced by entrepreneurs and small businesses.
- It can be built as a web platform within one semester.
- It supports several clear user types.
- It provides a meaningful use for AI without making AI responsible for final business decisions.
- It can be divided into three working software sprints.

## 3. Confirmed project decisions

The following decisions are confirmed by the latest project documents and discussion:

- The project is called Nashaa.
- The audience is Saudi entrepreneurs and small and medium-sized businesses.
- The product is a web platform.
- There are four application roles: business owner, innovator, investor, and administrator.
- The course uses three sprints.
- Sprint 1 covers accounts, profiles, dashboards, business ideas, and AI assessment.
- Sprint 2 covers business challenges, proposals, verification, communication, and investor matching.
- Sprint 3 covers collaboration progress, customer discovery, lead follow-up, ratings, reporting, administration, and final completion.
- The team has an updated charter, Sprint 1 design, branding, course requirements, and a survey with 64 responses.
- No source code, working application, test results, or repository export was included in the reviewed archive.

## 4. Items that are not confirmed

Do not assume these items are complete until direct evidence is provided:

- Application code
- A working deployment
- A GitHub repository and project board
- Completed Sprint 1 features
- Test cases and test results
- Bug records
- Final database choice
- Final AI provider
- Final hosting provider
- Real investor data
- Real customer lead data
- Approval of every planned feature by the supervisor

The chat said that application infrastructure had been started. This is a reported statement, not verified implementation evidence.

## 5. Users and what each user needs

### Business owner

A person preparing a business idea or operating a small business.

The business owner needs to:

- Create and manage an account.
- Maintain a business profile.
- Add and edit a business idea.
- Decide who can see the idea.
- Receive an AI-assisted business assessment.
- Turn a business need into a public challenge.
- Receive and compare proposals.
- Select an innovator.
- Discover possible investors.
- Define target customers.
- Save and track customer and investor leads.

### Innovator

A developer, designer, consultant, or service provider who helps businesses solve problems.

The innovator needs to:

- Create and manage a professional profile.
- Request account verification.
- Find business challenges.
- Filter challenges by relevant details.
- Submit a proposal.
- Communicate with a business owner when allowed.
- Update the progress of selected work.
- Mark work ready for completion.
- Rate a completed collaboration.

### Investor

A person who evaluates or funds business opportunities.

The investor needs to:

- Maintain investment interests and preferences.
- Optionally record previous investment categories or history.
- See suitable projects in ranked order.
- Understand why each project was suggested.
- Control contact preferences.
- Save interesting opportunities.

### Administrator

The administrator manages platform safety and participation.

The administrator needs to:

- Review verification requests.
- Approve or reject verification.
- Review reports about users, content, or interactions.
- Record decisions.
- Change permitted account or content status.
- View basic activity information.
- Keep a record of important administrative actions.

## 6. What the platform must not do

The project does not include:

- Payments or escrow
- Actual investment transactions
- Legal agreements
- Certified financial advice
- Guarantees of funding, customers, sales, or success
- Automatic messages sent without user approval
- A native mobile application
- A complete Arabic interface
- Purchasing or collecting restricted personal data
- Scraping private information
- Claiming that basic platform verification is official legal identity verification

## 7. Evidence from the requirements survey

The latest survey contains 64 consenting responses.

Respondent roles:

- 19 small-business owners
- 19 innovators or service providers
- 17 people preparing to become entrepreneurs
- 9 investors or people involved in investment evaluation

Most requested activities:

- Finding collaborators or suitable business projects: 22 selections
- Assessing a business idea: 21 selections
- Finding investors or investment opportunities: 20 selections
- Identifying practical next steps: 15 selections
- Finding potential customers: 12 selections
- Comparing proposals: 11 selections
- Tracking follow-up: 4 selections

Privacy findings:

- The largest group wanted a basic public summary while requiring approval before detailed information is shown.
- Other respondents preferred verified-user-only, registered-user-only, or private access.

Contact findings:

- The most common preferences were direct messages inside the platform and contact requests that must be accepted first.

Adoption concerns:

- Existing tools may already meet user needs.
- The platform may not have enough relevant users or opportunities.
- Users may worry about sharing business information.
- Setup effort and cost may discourage use.

Use the survey to justify requirements and priorities. Do not use survey responses as application user accounts or business records.

## 8. General development rules

Follow these rules for all sprints:

1. Every protected action must be checked by the server, not only hidden on the screen.
2. Users must not be able to read or change another user's private records.
3. Save important information before calling an AI service where possible.
4. If an AI request fails, do not delete the last successful result.
5. Clearly identify AI assumptions and uncertain information.
6. Show useful error messages instead of technical error text.
7. Keep screens usable on computers and common phone-sized screens.
8. Use clear labels and keyboard-accessible forms.
9. Keep secret keys outside source code.
10. Record data sources and permissions.
11. Use only permitted or clearly labeled fictional data for demonstrations.
12. Keep the written design consistent with the actual application.
13. Do not mark a feature complete until it works, has been tested, and can be demonstrated.

## 9. Suggested technical structure

The project documents propose:

- Web interface: Next.js
- Server application: Python with FastAPI
- Database: PostgreSQL or Firebase
- Source control: GitHub
- AI: an external large-language-model service

PostgreSQL is the preferred database unless working code already uses Firebase and changing it would create unnecessary delay.

The AI provider is not fixed. Place all AI calls behind one server component so the provider can be changed without rewriting the whole application.

The exact hosting provider is not fixed. Use a low-cost provider that supports secure connections, protected environment variables, application logs, and database backups.

## 10. Main information stored by the application

The final platform may need the following records. Sprint-specific records are introduced later.

### User account

- Account ID
- Email address
- Secure password information or external login identity
- Role
- Account status
- Verification status
- Created date
- Last updated date

Never store plain-text passwords.

### User profile

- Account ID
- Display name
- Location
- Short description
- Role-specific information
- Contact preference
- Profile visibility

### Business idea

- Idea ID
- Owner account ID
- Name or title
- Problem being solved
- Proposed solution
- Industry
- Business stage
- Target location
- Intended customers
- Available budget or expected cost range
- Current challenges
- Visibility setting
- Revision number
- Created and updated dates

### AI assessment

- Assessment ID
- Business idea ID
- Idea revision used
- Copy of the input used for generation
- Market considerations
- Target customer analysis
- Competitor considerations
- Indicative costs
- Suggested next steps or roadmap
- Assumptions
- Sources, when available
- Generation status
- Created date

Only save a successful assessment as the latest valid result.

## 11. Sprint 1 complete guide

### Sprint 1 goal

Create a working first version where a business owner can create an account, manage a profile, save a business idea, control its visibility, and receive or update a saved AI business assessment.

Sprint 1 must be working software. It cannot be only diagrams, screens, or written documentation.

### Sprint 1 user stories

#### US01 Create and access an account

A user can register, sign in, sign out, and access a personal workspace.

Completion checks:

- Valid registration creates an account.
- Invalid details show clear messages.
- A duplicate email is rejected.
- Valid login information opens the correct workspace.
- Invalid login information does not grant access.
- Signing out ends the session.

#### US02 Recover account access

A user can request a password reset and set a new password using a limited-time, single-use link or code.

Completion checks:

- A valid reset request can change the password.
- An expired request is rejected.
- A used request cannot be used again.
- Reset secrets are not stored as readable text.

#### US03 Maintain a profile

A user can update profile information suitable for the selected role.

Completion checks:

- Valid changes are saved and shown after reopening the profile.
- Users cannot edit another user's profile.
- Users cannot change their role through an ordinary profile update.

#### US04 Use a role-based dashboard

Each role sees relevant actions and information.

Completion checks:

- A business owner sees business ideas and assessment status.
- An innovator sees an appropriate empty or basic dashboard for later challenge features.
- An investor sees an appropriate empty or basic dashboard for later project features.
- An administrator sees permitted administrative entry points.
- Changing the page address manually does not bypass role restrictions.

#### US05 Submit and manage a business idea

A business owner can create, save, reopen, and edit a business idea.

Completion checks:

- Required fields are checked.
- The idea is connected to the correct owner.
- The owner can reopen and edit it.
- The revision number increases when assessment-related information changes.
- Another user cannot edit it.

#### US06 Receive a business assessment

A business owner can ask the platform to assess a saved idea.

The assessment must include:

- Market considerations
- Possible customers
- Competitor considerations
- Indicative costs
- Suggested development or launch steps
- Assumptions
- Sources when available

Completion checks:

- The screen shows that generation is in progress.
- A valid result follows the expected structure.
- A successful result is saved.
- Assumptions are clearly labeled.
- A failed request shows a useful message.

#### US07 Refine an assessment

A business owner can edit the idea and request an updated assessment.

Completion checks:

- The new result uses the updated idea.
- The application records which idea revision produced the assessment.
- Two assessment requests cannot accidentally run for the same idea at the same time.
- If updating fails, the previous successful assessment remains available.

#### US08 Control idea visibility

A business owner controls who can see an idea.

Minimum Sprint 1 choices:

- Private: owner only
- Registered users: signed-in users can see the permitted summary or details

A later version may add basic-summary-with-approval, verified-users-only, or selected-recipient access.

Completion checks:

- The setting is saved.
- Private information remains hidden from other users.
- The rule is checked by the server whenever the record is requested.

### Sprint 1 screens

Build at least these screens:

1. Registration
2. Login
3. Forgot password
4. Reset password
5. Profile view and edit
6. Role-based dashboard
7. Business idea list
8. Create business idea
9. Edit business idea
10. Business idea and assessment workspace
11. Assessment result view
12. Visibility setting
13. Useful error, loading, and empty states

### Sprint 1 data

Data structures already planned in the Sprint 1 design include:

- Accounts
- Profiles
- Sessions
- Password-reset requests
- Business ideas
- AI assessments

Create fictional data for development and testing:

- 12 to 20 test accounts across the four roles
- 10 to 15 fictional Saudi business ideas from different industries and stages
- Public and private ideas
- Ideas with incomplete information
- Edited versions of ideas
- Successful, delayed, failed, and incorrectly structured AI responses
- Valid, expired, used, and invalid password reset cases

Example fictional idea:

- Name: GreenBox
- Industry: Sustainable packaging
- Location: Riyadh
- Stage: Idea
- Problem: Small restaurants need affordable environmentally friendly packaging
- Target customers: Independent restaurants and cafes
- Estimated budget: SAR 50,000
- Visibility: Private

Do not use survey participants as users. Do not copy personal email addresses from the chat into the application.

### Sprint 1 development order

1. Create the student-owned repository and task board.
2. Confirm the database, AI provider, login method, and hosting choices.
3. Set up the web interface, server, database, and protected settings.
4. Create database tables and sample data.
5. Build registration, login, logout, sessions, and password reset.
6. Build profiles and role checks.
7. Build role-based dashboards.
8. Build business idea creation, viewing, editing, and visibility.
9. Build AI assessment generation and result checking.
10. Build assessment refinement and failure protection.
11. Connect all screens to the real server and database.
12. Deploy the working Sprint 1 version.
13. Run tests and fix critical defects.
14. Update diagrams to match the actual build.
15. Prepare the demonstration, review, and retrospective.

### Sprint 1 tests

Test at least:

- Successful and unsuccessful registration
- Duplicate email registration
- Successful and unsuccessful login
- Sign-out
- Valid, expired, invalid, and reused password reset
- Editing one's own profile
- Attempting to edit another profile
- Role restrictions through both the screen and direct server request
- Valid and invalid business ideas
- Saving and reopening an idea
- Editing an idea and increasing its revision
- Attempting to view or edit another user's private idea
- Successful AI assessment
- Delayed AI response
- AI service failure
- Invalid AI response structure
- Assessment update after editing an idea
- Previous assessment remaining after update failure
- Two assessment requests started close together
- Computer and phone-sized screen layouts
- Keyboard navigation and form labels
- Chrome, Edge, and Firefox

### Sprint 1 deliverables

- Working and deployed software
- Source code in a student-owned repository
- Task board showing owners and status
- Sprint goal
- US01 to US08 with acceptance criteria
- Task assignments
- Updated class or system structure diagram
- Use case diagram
- Sequence diagrams for important actions
- Entity relationship diagram
- Database schema
- Interface prototype updated to match the build
- Test cases with expected and actual results
- Bug list with status
- Demonstration record and supervisor feedback
- Sprint review
- Sprint retrospective
- Individual contribution table with evidence

### Sprint 1 is complete only when

- US01 to US08 work in the integrated application.
- The application can be demonstrated from the actual system.
- Private information cannot be accessed by unauthorized users.
- A failed AI request does not destroy saved work.
- Critical defects are fixed.
- Tests show actual results.
- The design documents match the implementation.
- Each student has clear contribution evidence.

## 12. Sprint 2 complete guide

### Sprint 2 goal

Allow a business owner to publish a challenge, allow a verified innovator to find it and submit a proposal, allow the owner to select a collaborator, and allow businesses and investors to discover suitable matches.

### Sprint 2 user stories

#### US09 Publish a business challenge

The owner creates a challenge from a business need. The owner must review and approve the content before publication.

Store:

- Challenge title
- Business or idea reference
- Problem description
- Desired result
- Required skills
- Optional budget or compensation information
- Expected timeline
- Status: draft, published, closed

#### US10 Find suitable challenges

Innovators can browse published challenges and filter them by useful details such as skill, industry, location, or status.

#### US11 Submit a proposal

Only an approved, verified innovator may submit a proposal to an open challenge.

Store:

- Proposed approach
- Deliverables
- Timeline
- Optional cost
- Innovator
- Challenge
- Submission status

#### US12 Compare and select proposals

The owner sees proposals in a comparable format and selects one collaborator.

Only the challenge owner can select. The platform must prevent conflicting active selections.

#### US13 Request and receive verification

A user submits a verification request. An administrator approves or rejects it. The result changes the actions available to the user.

This is platform approval, not official government identity verification, unless a real approved method is later added.

#### US14 Communicate inside the platform

Eligible users can exchange messages when their roles, verification status, and contact permissions allow it.

Keep the first version simple. Do not add voice, video, file sharing, or external messaging unless the core system is already stable.

#### US15 Find suitable investors

Business owners receive investor suggestions with a clear reason for each match.

Possible matching factors:

- Industry
- Business stage
- Location
- Funding range
- Investor preferences
- Previous investment categories, when available

#### US16 Discover relevant projects

Investors save preferences and see a ranked project list. The platform must explain each match and respect business visibility settings.

### Sprint 2 data

New records:

- Challenges
- Verification requests
- Proposals
- Collaborations
- Conversations
- Messages
- Investor preferences
- Previous investment categories or history
- Match results and match reasons

No real investor dataset was included in the source archive.

Use one of these sources:

1. Permitted public data with recorded source and terms.
2. Data provided with permission.
3. Clearly labeled fictional demonstration data.

For the semester prototype, begin with fictional investor profiles if real, reliable data is unavailable.

Suggested fictional dataset:

- 15 to 25 investor profiles
- Several industries and business stages
- Different funding ranges
- Different locations and preferences
- Some investors with history and some without history
- 10 to 20 challenges
- 2 to 5 proposals per test challenge
- Approved, pending, and rejected verification requests

### Sprint 2 development order

1. Review Sprint 1 feedback and fix remaining important defects.
2. Add challenge records and screens.
3. Add challenge browsing and filters.
4. Add verification request and administrator review.
5. Add proposal submission.
6. Add proposal comparison and selection.
7. Add simple authorized messaging.
8. Add investor preferences and project information required for matching.
9. Build a clear, rule-based matching score.
10. Show match explanations.
11. Test complete business-owner, innovator, investor, and administrator journeys.
12. Deploy and demonstrate the Sprint 2 version.

### Matching approach

Start with understandable rules rather than a hidden AI score.

Example:

- Industry match: 35 points
- Business-stage match: 25 points
- Funding-range match: 20 points
- Location preference: 10 points
- Similar previous investment: 10 points

The exact values must be decided and documented. Show users the factors that caused a match. If history is missing, match using current preferences and say that history was unavailable.

### Sprint 2 tests

Test at least:

- Challenge creation, editing, publishing, and closing
- Only published challenges appearing in discovery
- Filters returning correct results
- Unverified innovator blocked from proposal submission
- Verified innovator allowed to submit
- Proposal connected to the correct challenge and innovator
- Only the owner selecting a proposal
- Prevention of two active selections
- Messaging allowed and denied under correct conditions
- Conversation privacy
- Administrator verification approval and rejection
- Matching with complete and missing investor data
- Clear match explanations
- Visibility rules applied to investor project results
- Regression of all important Sprint 1 features

### Sprint 2 deliverables

Produce the same evidence types as Sprint 1:

- Working software
- Updated backlog and assignments
- Updated diagrams and database design
- Actual tests and results
- Bug list
- Demonstration and feedback
- Sprint review and retrospective
- Individual contribution evidence

### Sprint 2 scope reduction order

If time becomes limited, reduce features in this order:

1. Remove advanced message features; keep simple text messages.
2. Reduce the number of filters.
3. Use rule-based matching without advanced AI.
4. Use fictional investor data.

Do not remove:

- Server-side permissions
- Verification checks for proposals
- Proposal ownership and selection rules
- Visibility protection
- Match explanations
- Testing

## 13. Sprint 3 complete guide

### Sprint 3 goal

Finish collaboration tracking, customer discovery, lead follow-up, ratings, issue handling, administration, system hardening, evaluation, final deployment, and final academic material.

### Sprint 3 user stories

#### US17 Track collaborative work

The selected business owner and innovator can add progress updates. The innovator can mark work ready, and the owner confirms completion.

#### US18 Define target customers

The business owner generates and edits a target-customer profile based on the saved business idea.

Possible fields:

- Customer type
- Industry
- Location
- Size
- Main need
- Buying motivation
- Likely objections
- Useful acquisition channels

#### US19 Discover potential customers

For business-to-business ideas, the owner may use permitted company records or an uploaded list with recorded source information.

For consumer-focused ideas, the platform should suggest customer groups and acquisition channels instead of pretending to provide personal leads.

#### US20 Prepare an outreach draft

The platform creates a draft message using the business and selected lead context. The owner can edit and copy it.

The platform must not automatically send the message.

#### US21 Manage lead follow-up

The owner saves customer and investor leads, adds notes, and updates status.

Suggested statuses:

- New
- Reviewing
- Contact requested
- Contacted
- Interested
- Not interested
- Follow-up needed
- Closed

#### US22 Rate completed collaboration

Only participants in a completed collaboration can rate it. Each participant may submit one rating per collaboration.

#### US23 Report a platform issue

A user reports an inappropriate account, content item, or interaction. The report includes a category, description, and related record.

#### US24 Manage platform activity

An administrator reviews reports, records decisions, changes permitted account or content status, and sees a record of important actions.

### Sprint 3 data

New records:

- Collaboration progress updates
- Customer profiles
- Customer leads or imported company records
- Lead source information
- Outreach drafts
- Lead notes and statuses
- Ratings
- User reports
- Administrator decisions
- Administrative action records
- Evaluation sessions and KPI results

No usable customer lead dataset was included in the archive.

Use:

- Permitted public company records
- User-uploaded lists for which the user has permission
- Clearly labeled fictional demonstration data

Do not collect private personal data or create consumer contact lists without permission.

### Sprint 3 development order

1. Fix important Sprint 2 feedback and defects.
2. Add collaboration progress and completion.
3. Add target-customer profiles.
4. Add permitted lead import or fictional lead data.
5. Add customer suggestions and clear source labels.
6. Add editable outreach drafts.
7. Add customer and investor lead tracking.
8. Add ratings for completed collaborations.
9. Add user reports and administrator review.
10. Add administrative action records.
11. Add backup/export and test restoring saved data.
12. Run complete security, browser, accessibility, failure, and end-to-end tests.
13. Conduct user evaluation and calculate project measures.
14. Fix critical defects and freeze the final version.
15. Complete the final report, user guide, presentation, and demonstration.

### Sprint 3 tests

Test at least:

- Progress updates restricted to collaboration participants
- Correct work-ready and completion transitions
- Customer profile generation, editing, and saving
- Valid and invalid lead files
- Source information retained for imported leads
- Consumer idea receiving segments rather than personal contacts
- Outreach draft generation and editing
- AI failure not deleting saved leads
- Duplicate lead handling
- Lead notes and statuses saved correctly
- Ratings blocked before completion or from nonparticipants
- One rating per participant per collaboration
- User report submission
- Administrator report decisions
- Administrative action record creation
- Data backup and successful restore
- End-to-end journeys for all roles
- Important Sprint 1 and Sprint 2 regression tests
- Browser and phone-sized layouts
- Keyboard access and readable color contrast
- Application behavior when AI or another external service is unavailable

### Sprint 3 project measures

The charter proposes these measures:

- All final high-priority stories meet their completion checks.
- At least 80 percent of attempted core tasks are completed without help during user testing.
- At least 70 percent of reviewed top-five recommendations are judged relevant using agreed factors.
- At least 80 percent of sampled AI assessments pass a checklist for completeness, consistency, and clear assumptions.
- Average user rating is at least 4 out of 5 for clarity and usefulness.
- All planned access and visibility tests pass before deployment.
- Core workflows complete without unhandled errors or loss of saved information under the tested workload.

Always report the number and roles of participants, tested browsers, tested workload, and unresolved limitations with the results.

### Sprint 3 deliverables

- Final deployed application
- Final source code
- Final database and backup/restore instructions
- Final diagrams matching the application
- Complete test evidence and defect status
- User evaluation and project measures
- Requirement-to-test traceability table
- User guide
- Final report
- Final demonstration and presentation
- Sprint review and retrospective
- Individual contribution evidence

### Sprint 3 scope reduction order

If the project is behind schedule:

1. Defer advanced outreach drafting.
2. Defer ratings.
3. Reduce customer lead features to permitted file import plus segment suggestions.
4. Keep administrative reporting simple.

Do not sacrifice:

- Working end-to-end core journeys
- Permissions and privacy
- Saved-data reliability
- Testing
- Deployment
- Academic evidence

## 14. Complete three-sprint dependency order

Build features in this order because later features depend on earlier ones:

1. Accounts and sessions
2. Profiles and roles
3. Dashboards
4. Business ideas
5. Visibility controls
6. AI assessments
7. Verification
8. Challenges
9. Proposals
10. Collaborator selection
11. Messaging
12. Investor preferences
13. Investor and project matching
14. Collaboration progress
15. Customer profiles
16. Customer suggestions or permitted leads
17. Lead follow-up
18. Ratings
19. User reports and administration
20. Full evaluation and final delivery

Do not begin complex Sprint 3 work while Sprint 1 security or data-saving problems remain unresolved.

## 15. Team responsibility model

The updated charter still uses student placeholders. Replace them with actual names and IDs.

Suggested responsibility split:

- Student A: sprint coordination, task board, interface integration, and deployment
- Student B: server functions, business workflows, and AI assessment
- Student C: interface, challenge and proposal screens, and usability
- Student D: database, investor matching, and customer lead features
- Student E: login, administration, access testing, quality records, and evaluation

All students must contribute to building and testing. Documentation alone is not enough evidence of software contribution.

For each student, keep:

- Assigned tasks
- Repository commits
- Reviewed changes
- Completed tests
- Written or updated design sections
- Demonstrated features
- Problems solved

## 16. Definition of complete

A feature is complete only when:

- It works in the integrated application.
- It meets its written completion checks.
- The server checks access and input rules.
- It has repeatable tests with actual results.
- Related old features still work.
- Its code has been reviewed and merged.
- It can be shown in the deployed or integrated version.
- Known problems are recorded.
- The design and database documents match it.
- The responsible student can explain it.

Do not describe a planned feature, design screen, or unfinished prototype as implemented.

## 17. Information security and privacy

The original archive contains personal emails, meeting links, Google Form links, a Lovable project link, names, survey timestamps, and payment discussions.

Do not place these details in source code, public repositories, demonstration data, or academic reports.

Required protections:

- Remove or hide personal email addresses from shared reports.
- Anonymize survey responses.
- Replace exposed project links when needed.
- Keep API keys and database passwords in protected environment settings.
- Use fictional names and contact details in demonstrations.
- Give users the least access needed for their role.
- Record important administrator actions without storing unnecessary sensitive information.
- Use secure web connections for the deployed application.
- Test backup and restoration.

## 18. Open decisions that require confirmation

Ask the supervisor or project team to confirm:

1. Exact dates and required files for all three sprints
2. Whether Sprint 1 is late and what recovery plan is expected
3. Whether the updated charter is accepted
4. Whether 64 survey responses are enough
5. Whether survey analysis belongs in the charter or final appendix
6. Whether a computer science student needs separate documentation
7. Whether all 24 stories are required or may be formally reduced
8. Whether fictional investor and customer data are acceptable for the prototype
9. Whether external developers or paid support are permitted under academic rules
10. What evidence of each student's contribution is required
11. Any required hosting location, data location, or privacy restrictions

## 19. Immediate next actions

The next AI model or project team should do the following before adding new features:

1. Obtain the current code, repository, task board, prototype, deployment, and service-account access.
2. Compare the actual code with Sprint 1 stories US01 to US08.
3. List what is complete, incomplete, broken, or missing.
4. Confirm database, AI, login, and hosting choices.
5. Add student names, IDs, supervisor name, and real responsibilities to the charter.
6. Put all 24 stories into the task board with owners and sprint assignments.
7. Finish and test Sprint 1 before beginning major Sprint 2 development.
8. Analyze the 64 survey responses and record which requirements changed because of them.
9. Create a traceability table connecting each story to its design, code, and tests.
10. Prepare actual working demonstrations rather than screenshots alone.

## 20. Final instruction to the next AI model

Keep the project simple, honest, and demonstrable.

Do not add features because they sound impressive. Build the agreed stories in dependency order. Protect private information. Use fictional data when real data is unavailable or restricted. Explain every recommendation. Test every completed feature. Keep the documents consistent with the software.

The immediate priority is a working, tested Sprint 1 covering US01 to US08. After that, implement Sprint 2 collaboration and investor discovery. Finish with Sprint 3 customer discovery, administration, evaluation, and final delivery.

## 21. Project setup answers for an AI developer

Use the following answers if an AI developer asks what is being built, which technology to use, whether code already exists, or what the finished project should do.

### What is being built

Nashaa is a responsive web platform for Saudi entrepreneurs and small and medium-sized businesses.

It is a complete web application with:

- A user-facing website
- A server that handles application rules and protects data
- A database
- An external AI service for business assessments and selected text suggestions
- Separate workspaces for business owners, innovators, investors, and administrators

It is not only a public information website, an AI chat page, a mobile application, or a reusable code library.

### Recommended technology

The current project documents propose:

- Web interface: Next.js
- Server: Python with FastAPI
- Database: PostgreSQL
- Source control and task tracking: GitHub
- AI: one external large-language-model service called only through the server
- Hosting: a low-cost service that supports secure connections, protected settings, logs, and backups

PostgreSQL is recommended over Firebase because the project contains many connected records, including users, ideas, assessments, challenges, proposals, collaborations, messages, leads, ratings, and reports.

However, do not rebuild working code only to follow this recommendation. First inspect any existing implementation. If it already uses Firebase correctly and changing it would delay the project, document that decision and continue with Firebase.

The final choices for the database, AI provider, login method, and hosting service have not been confirmed in the supplied materials. Record each final choice and its reason before completing Sprint 1.

### Current state

The project is not at the idea stage. Planning and design work already exist.

Available materials include:

- Approved Nashaa project concept
- Project proposal
- Updated project charter
- Functional and quality requirements
- 24 user stories with completion checks
- Three-sprint plan
- Sprint 1 design and database diagrams
- Course requirements and grading rubric
- Brand identity and logo files
- Requirements survey with 64 responses

The chat says that application infrastructure was started and that a high-quality interface prototype was created. These claims were not supported by source code or a running application in the supplied archive.

The reviewed archive does not contain:

- Source code
- A repository export
- A running application link
- A confirmed database
- Completed tests or test results
- A bug list
- A completed sprint review
- Clear student contribution evidence

Therefore, do not automatically start from scratch and do not automatically assume working code exists. The first action must be to obtain and inspect the current repository, prototype, deployment, database, and task board. Reuse sound existing work, then fill the missing Sprint 1 requirements.

### Finished-project goal and scope

The finished Nashaa platform should allow the following complete journeys.

#### Business owner journey

1. Register and sign in.
2. Complete a business profile.
3. Create and save a business idea.
4. Control who can see the idea.
5. Receive and refine an AI-assisted business assessment.
6. Publish a business challenge.
7. Receive, compare, and select an innovator proposal.
8. Communicate and track collaboration progress.
9. Discover suitable investors with clear match reasons.
10. Define target customers and review permitted leads or suggested customer groups.
11. Save customer and investor leads and track follow-up.

#### Innovator journey

1. Register and create a professional profile.
2. Request platform verification.
3. Browse and filter published challenges.
4. Submit a proposal after verification.
5. Communicate with an authorized business owner.
6. Update selected collaboration progress.
7. Mark work ready for completion.
8. Rate a completed collaboration.

#### Investor journey

1. Register and create an investment profile.
2. Save industry, stage, location, and funding preferences.
3. View ranked business opportunities.
4. Understand why each opportunity was suggested.
5. Save interesting opportunities and use the permitted contact method.

#### Administrator journey

1. Sign in through an administrator account.
2. Review verification requests.
3. Approve or reject requests.
4. Review reports about users, content, or interactions.
5. Record decisions and apply permitted account or content actions.
6. Review a record of important administrator actions.

### Minimum acceptable final result

The project is successful only if it includes:

- A deployed and working web application
- Complete core journeys for all four roles
- Protected user and business information
- Saved data that remains available after signing out and returning
- Clear handling of AI failures and incomplete data
- Transparent investor and customer recommendations
- Tests with actual results
- A recorded bug list and resolution status
- Diagrams and written requirements that match the real application
- A user guide and final demonstration
- Clear evidence of each student's work

### Important scope limits

Do not add payments, escrow, investment transactions, legal agreements, automatic outreach, native mobile applications, or restricted-data collection.

If time is limited, prioritize complete and secure user journeys over extra features. Outreach drafts and collaboration ratings are the first planned features that may be deferred. Login, permissions, business ideas, AI assessment, challenges, proposals, matching, saved data, testing, and deployment must remain protected priorities.
