# OLD  DIVISION OF LABOUR (IGNORE)

Our team uses a **Vertical Feature Ownership** structure. You will build and own your assigned feature end-to-end (full-stack), writing both the backend logic and the frontend components for it.

---

### Timu (PM)
**Role:** Project Manager + Auth & Home Page Banner  
**Focus Area:** Project management, User Authentication, and Home Dashboard layout.

* **Weeks 1–3 (MVP 1):** Repository setup, GitHub Kanban board, and User Registration / Login / Logout API endpoints & UI forms with authentication state handling.
* **Weeks 4–6 (MVP 2):** Home Page dashboard structure and "Urgent Application Banners" (e.g., alert cards for *"Hurry! [Company] closes today!"*).
* **Weeks 7–8 (MVP 3):** Connecting live backend stats to Home Page metric cards, responsive mobile/desktop layout pass.
* **Week 9 (Finals):** Coordinating the 10–12 min Loom video script, architecture diagram, and final submission checks.

---

### Member 2
**Role:** Application Tracker Backend & Priority Engine  
**Focus Area:** Database Schema, Job Application CRUD, and Core Priority Algorithm.  
**Best Fit For:** Someone interested in database design, complex SQL queries, REST API construction, and writing unit tests for logic.

* **Weeks 1–3 (MVP 1):** Core relational database schema (`users`, `applications`, `cvs`, `friends`), SQL migration scripts, and CRUD REST endpoints for applications (`POST`, `GET`, `PUT`, `DELETE`).
* **Weeks 4–6 (MVP 2):** The Application Priority Sorting Engine algorithm (sorting rolling deadlines approaching target dates vs. upcoming fixed dates) with comprehensive unit tests for edge cases.
* **Weeks 7–8 (MVP 3):** Backend search query optimizations and assist on bug fixes for the final application board logic.
* **Week 9 (Finals):** Loom video section on DB architecture and backend priority logic.

---

### Member 3
**Role:** Application Tracker Frontend & Filtering UI *(Available)*  
**Focus Area:** Core Application Tracker Board, Sorting/Filtering Controls, and Modal Forms.  
**Best Fit For:** Someone interested in frontend components, user interface design, state management, and interactive data tables.

* **Weeks 1–3 (MVP 1):** Main application table layout, "Add Job Application" modal form (Company, Role, Link, Deadline, Is Rolling toggle).
* **Weeks 4–6 (MVP 2):** Interactive status badges (Applied, Interviewing, Offer, Rejected) with inline status editing, sorting & filtering controls (filter by status, sort by priority/deadline).
* **Weeks 7–8 (MVP 3):** Instant search bar for filtering job applications by Company/Role, table UI polish, empty state indicators.
* **Week 9 (Finals):** Loom video section showcasing the core Application Tracker workflow.

---

### Member 4
**Role:** CV Version Manager & Custom PDF Exporter  
**Focus Area:** File Upload handling, Linking CVs to Job Postings, and Custom PDF Exports.  
**Best Fit For:** Someone interested in file handling systems, relational mapping (linking CVs to jobs), and dynamic file generation.

* **Weeks 1–3 (MVP 1):** Backend endpoint for handling PDF uploads (`POST /api/cvs/upload`) with file validation, and initial CV list component.
* **Weeks 4–6 (MVP 2):** Database relationships linking CV records to specific job postings, Drag-and-Drop file upload dropzone UI, and PDF preview modal.
* **Weeks 7–8 (MVP 3):** Dynamic Custom PDF Export Handler (allows downloading CVs with custom filenames like `CV_<Name>_<Role>.pdf` without modifying the original stored file) and rendering `"Sent to: [Job Badges]"` labels on the CV page.
* **Week 9 (Finals):** Loom video section demonstrating CV uploads, job linking, and PDF custom exports.

---

### Member 5
**Role:** Social Network, AI Assistant & DevOps  
**Focus Area:** Friend Search/Invite System, Privacy Controls, AI Feature (with Fallback), Deployment & CI/CD.  
**Best Fit For:** Someone interested in social features/permissions, cloud deployment (Render/Vercel), Docker/GitHub Actions, and AI API integrations.

* **Weeks 1–3 (MVP 1):** Environment setup (Docker / CI GitHub Actions), setting up staging/production deployment pipeline on Render/Vercel.
* **Weeks 4–6 (MVP 2):** Home Page stats SQL aggregation queries (`total_applied_this_week`, `active_applications`), AI Cover Letter/Resume tip generator endpoint with strict offline/mock fallback handling.
* **Weeks 7–8 (MVP 3):** "Your Friends" page UI and API (Add friend, accept request), granular privacy toggle settings (Share weekly stats vs. Share full read-only job board).
* **Week 9 (Finals):** Verifying cloud deployment stability, Loom video section explaining deployment pipeline and AI fallback logic.
