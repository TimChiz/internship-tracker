# ROADMAP AND TIMELINE

## Overall Roadmap

| Week / Dates | Phase & Milestone | Key Deliverables & Owner Focus |
| :--- | :--- | :--- |
| **Week 1**<br>(Oct 3 – Oct 11) | Project Setup & Architecture | - Repo setup, GitHub Projects board setup (PM)<br>- DB Schema design & REST API routes definition (Team)<br>- Environment & branching strategy setup |
| **Week 2**<br>(Oct 12 – Oct 18) | Core Feature Foundations | - User Signup/Login Auth endpoints & UI (PM)<br>- Application CRUD endpoints & DB tables (Member 2)<br>- Base UI layout & Application table (Member 3) |
| **Week 3**<br>(Oct 19 – Oct 25) | MVP 1 Completion | - Connect Auth to application dashboard (PM & Member 3)<br>- CV upload backend handling (Member 4)<br>- Basic deployment pipeline test (Member 5)<br>🚩 **MVP 1 Tagged on GitHub (v1.0-MVP1)** |
| **Week 4**<br>(Oct 26 – Nov 1) | Sorting & Urgent Logic | - Priority sorting algorithm for rolling deadlines (Member 2)<br>- Urgent application banners on Home Page (PM)<br>- CV-to-Application linking DB relationships (Member 4) |
| **Week 5**<br>(Nov 2 – Nov 8) | CV Manager & Social Engine | - Drag-and-drop CV interface (Member 4)<br>- Friend invite/search API endpoints (Member 5)<br>- Stats aggregation SQL queries (Member 5) |
| **Week 6**<br>(Nov 9 – Nov 15) | MVP 2 Completion | - AI cover letter / resume tip generator + offline fallback (Member 5)<br>- Custom PDF title renaming logic (Member 4)<br>- Intermediary code reviews & unit testing (Team)<br><br>🚩 **MVP 2 Tagged on GitHub (v2.0-MVP2)** |
| **Week 7**<br>(Nov 16 – Nov 22) | Social Features & Privacy | - Friend Dashboard UI & privacy toggle controls (Member 5)<br>- Advanced filtering & search on Application board (Member 3)<br>- Home page stats dashboard polish (PM) |
| **Week 8**<br>(Nov 23 – Nov 30) | MVP 3 (Final App Version) | - Full CSS/UI polish & bug fixes across all pages (Team)<br>- Production deployment verification on Vercel/Render (Member 5)<br>- End-to-end integration testing (Team)<br>🚩 **MVP 3 Tagged on GitHub (v3.0-MVP3)** |
| **Week 9**<br>(Dec 1 – Dec 7) | Final Course Deliverables | - Record & edit 10–12 min Loom Demo Video (All members speak)<br>- Draw Non-Shared Architecture Diagram<br>- Compile individual PDF reports (PR links & review links) |
| **Buffer**<br>(Dec 8 – Dec 14) | Final Submission Safety Margin | - Final check before strict deadline on Dec 14 |

---

## Detailed Timeline

### Phase 1: Foundation, Setup & MVP 1 (Oct 3 – Oct 25)

#### Week 1: Architecture & Repository Initialization (Oct 3 – Oct 11)
* **PM (You):**
  * Set up GitHub repo, main branch protection rules, and PR description template.
  * Create the GitHub Projects Kanban board with columns: Backlog, To Do, In Progress, PR Review, Done.
  * Draft project coding conventions (file naming, git commit style, branching strategy).
* **Member 2 (Backend Core):**
  * Design initial relational database schema (`users`, `applications`, `cvs`, `friends`).
  * Create SQL setup scripts / ORM migration files.
  * Define REST API routes and JSON request/response formats.
* **Member 3 (Frontend Core):**
  * Initialize Frontend framework (React / Next.js / Vue) repository folder structure.
  * Define global styling, CSS theme (colors, fonts), and reusable UI layout components (Navbar, Sidebar).
* **Member 4 (CV Manager Specialist):**
  * Research file storage solution (local file system upload vs Cloud storage).
  * Design DB tables for storing uploaded CV metadata (filename, original title, upload timestamp).
* **Member 5 (DevOps, AI & Social):**
  * Set up Docker containerization / local environment setup guides.
  * Create GitHub Actions CI pipeline to run automated linting and tests on every Pull Request.

#### Week 2: Auth & Core CRUD Endpoints (Oct 12 – Oct 18)
* **PM (You):**
  * Build `/api/auth/register`, `/api/auth/login`, and `/api/auth/logout` API endpoints.
  * Build User Signup and Login UI forms with client-side validation.
* **Member 2 (Backend Core):**
  * Implement CRUD REST endpoints for applications: `POST /api/applications`, `GET /api/applications`, `PUT /api/applications/:id`, `DELETE /api/applications/:id`.
  * Write unit tests for application CRUD endpoints.
* **Member 3 (Frontend Core):**
  * Build Application Tracker main page table view layout.
  * Build "Add Job Application" Modal form (Company, Role, Link, Application Deadline, Is Rolling toggle).
* **Member 4 (CV Manager Specialist):**
  * Build backend endpoint for handling PDF file uploads (`POST /api/cvs/upload`).
  * Add backend validation to ensure uploaded files are valid PDFs under size limits.
* **Member 5 (DevOps, AI & Social):**
  * Set up initial deployment staging environment on Render / Vercel.
  * Verify database connections in the cloud deployment environment.

#### Week 3: Wiring, Testing & MVP 1 Release (Oct 19 – Oct 25)
* **PM (You):**
  * Implement route protection middleware (redirect unauthenticated users to Login).
  * Connect Auth state to frontend layout (display user avatar / logout button).
* **Member 2 & 3 (Backend & Frontend Co-working):**
  * Connect Frontend Add/Edit Application form to the Backend REST API.
  * Implement empty state UI when a user has zero job applications logged.
* **Member 4 (CV Manager Specialist):**
  * Build simple frontend list component displaying all uploaded CV files.
* **Member 5 (DevOps):**
  * Run end-to-end deployment verification.
* **Team Milestone:**
  * 🚩 **Tag `v1.0-MVP1` on GitHub repository.**

---

### Phase 2: Core Features & MVP 2 (Oct 26 – Nov 15)

#### Week 4: Priority Engine & Home Page Layout (Oct 26 – Nov 1)
* **PM (You):**
  * Design and build Home Page dashboard grid structure.
  * Build "Urgent Application Banners" component (e.g., *"Hurry! [Company Name] closes today!"*).
* **Member 2 (Backend Core):**
  * Build application priority algorithm (Sort logic: Rolling applications approaching target date first, then upcoming fixed deadlines chronologically).
  * Write unit tests testing priority sorting calculations with edge-case dates.
* **Member 3 (Frontend Core):**
  * Add sorting and filtering controls to Applications Tracker UI (Filter by Status: Applied, Interviewing, Rejected; Sort by Priority).
* **Member 4 (CV Manager Specialist):**
  * Build database relationship linking `cv_id` to specific job application records.
  * Add "Select CV Submitted" dropdown inside the "Add Application" modal.
* **Member 5 (DevOps, AI & Social):**
  * Write SQL aggregation queries for Home Page stats (`total_applied_this_week`, `total_active_applications`, `response_rate`).

#### Week 5: CV Drag-and-Drop & Social Backend (Nov 2 – Nov 8)
* **PM (You):**
  * Wire backend stats queries to Home Page visual metric cards.
* **Member 2 (Backend Core):**
  * Design and create database schema for Friends system (`friendships` table with `user_id_1`, `user_id_2`, `status`: pending/accepted, `privacy_level`).
* **Member 3 (Frontend Core):**
  * Add status badges with color coding (Green = Offer, Yellow = Interviewing, Red = Rejected) with quick inline editing.
* **Member 4 (CV Manager Specialist):**
  * Build Drag-and-Drop upload dropzone UI on CV Manager page.
  * Build PDF file view modal component.
* **Member 5 (DevOps, AI & Social):**
  * Build backend friend request endpoints (`POST /api/friends/request`, `POST /api/friends/accept`, `GET /api/friends`).

#### Week 6: AI Integration, Custom PDF Exporter & MVP 2 Release (Nov 9 – Nov 15)
* **PM (You):**
  * Perform code review audit across all open PRs to ensure self-contained descriptions and docstrings.
* **Member 2 & 3 (Core Team):**
  * Refine search bar UI to instantly filter applications by Company or Role name.
* **Member 4 (CV Manager Specialist):**
  * Implement custom PDF export download handler: dynamically set response headers so file downloads as `CV_<UserName>_<JobRole>.pdf` without mutating stored file.
* **Member 5 (DevOps, AI & Social):**
  * Implement AI Assistant API (e.g., LLM cover letter / resume feedback tips) with a strict fallback check: if no `LLM_API_KEY` exists in env, return structured pre-written mock suggestions.
* **Team Milestone:**
  * 🚩 **Tag `v2.0-MVP2` on GitHub repository.**

---

### Phase 3: Social Network, Privacy & MVP 3 (Nov 16 – Nov 30)

#### Week 7: Friends Page & Granular Privacy Controls (Nov 16 – Nov 22)
* **PM (You):**
  * Responsive CSS design pass on Home Page and Auth screens (mobile/desktop support).
* **Member 2 & 4 (CV Linkage):**
  * On CV Manager page, render dynamic label: `Sent to: [List of Application Badges]` linking back to specific job records.
* **Member 3 & 5 (Social & Privacy Team):**
  * Build "Your Friends" Page UI (Add friend input bar, pending invitation notifications).
  * Build Privacy Toggle settings when accepting friend requests (Option A: Share weekly stats only vs Option B: Share full job board).
  * Build Friend Board Modal view (Read-only view of friend's applications table with sensitive notes and CV links hidden).

#### Week 8: End-to-End Polish, Testing & MVP 3 Release (Nov 23 – Nov 30)
* **All Members:**
  * Complete team "Bug Bash" (fixing UI alignment issues, broken links, date formatting bugs).
  * Review all PRs to ensure 100% of review comments have been resolved or refuted.
* **Backend Devs (Members 2, 4, 5):**
  * Finalize unit test suite coverage for priority logic, file export renamer, and privacy checks.
* **Member 5 (DevOps):**
  * Verify live production deployment URL is stable, fast, and accessible without API keys.
* **Team Milestone:**
  * 🚩 **Tag `v3.0-MVP3` (Final Version) on GitHub repository.**

---

### Phase 4: Final Deliverables & Video Production (Dec 1 – Dec 7)

#### Dec 1 – Dec 3: Group Loom Video Recording
* Draft 10–12 minute video script highlighting: account creation, login, job tracking, priority logic, CV management, social features, AI fallback, tech stack overview, and deployment.
* Record video ensuring all 5 members present a section.
* Dedicate 3–5 minutes explaining MVP 1 ➔ MVP 2 ➔ MVP 3 progression and feature pivots.

#### Dec 4 – Dec 5: Architecture Diagram
* Draw non-shared architecture diagram.
* Clearly label `#separationofconcerns` and explain `#abstraction` layers (UI ➔ Controller ➔ Service ➔ DB).

#### Dec 6 – Dec 7: Individual Submission PDFs
Each member compiles their individual PDF report containing:
1. Links to meaningful PRs created/coded.
2. Links to PR reviews with constructive feedback.
3. Links to assigned GitHub Kanban tasks.
4. Equal team role descriptions.

---

### Buffer (Dec 8 – Dec 14)
* **Final Submission Safety Margin:** Final check before strict deadline on Dec 14.