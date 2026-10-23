# QueuExpress: Government Agency Queue Tracker

**Course:** CCC181 · Week 1 Proposal
**Author:** Zalsos, Julius G.

---

## 1. Problem Statement

When queueing for services in government agencies, which for this specific proposal's focus being the Philippine Statistics Authority in Iligan City, people wait in line for hours on end in order to get processed. Problems may occur when the individualing waiting in line does not have the free time in their day as they have other responsibilities as well.

- Citizens repeatedly interrupt counter staff to ask for queue updates or miss overhead announcements in crowded, noisy lobbies as said announcement is only done by voice.
- People waiting risk losing their turn or wasting an entire day off if they step away briefly to attend to young children or step outside.
- There is no real-time visibility into queue progression or estimated position, forcing citizens to stand idly in the office lobby without knowing when they will be served.

**QueuExpress** is a web app that allows citizens to join the queue digitally and monitor their ticket status and position in real time on their phone, while enabling agency staff to filter, call, and process applicants efficiently from a simple desktop dashboard.

## 2. Setting

The Philippine Statistics Authority provincial office in Iligan City, operating Mondays to Fridays from 8:00 AM to 5:00 PM. The office features multiple service windows staffed by desk officers using desktop PCs. Daily workflow involves handling a high volume of walk-in citizens applying for civil registry documents (birth, marriage, and death certificates) and submitting PhilSys National ID application requirements. The physical environment consists of a crowded, noisy lobby where applicants currently rely on paper queue tickets and overhead announcements done by voice to know when to approach the counter.

## 3. Stakeholders and User Profiles

### Applicant
- **Who:** Working parent or adult citizen visiting the agency on limited free time due to their work shift or other responsibilities.
- **Goals:** Submit required ID application documents efficiently, monitor line progression in real time, and avoid standing around in a crowded, noisy lobby.
- **Pain points:** Long, unpredictable wait times; missing hard-to-hear audio announcements; fear of losing his place in line or wasting a rare day off
- **Needs:** Fast mobile join form, prominent display of ticket number and live queue position, single-thumb operable buttons, and real-time status updates that don't require manual page refreshing.

### Agency Staff
- **Who:** Counter Officer at the PSA Iligan City office operating a desktop PC at desk counters from 8:00 AM to 5:00 PM. Has differing tech comfort and readin struggles depending on their age bracket.
- **Goals:** Call waiting applicants in order, process document verification and biometrics smoothly, filter queue lists by assigned counter service, and update ticket statuses in one click to maintain continuous workflow.
- **Pain points:** Eye strain from small fonts and cluttered legacy UI; frequent interruptions from confused citizens asking about their numbers; wasted time searching lists when applicants fail to hear overhead announcements in a noisy lobby. 
- **Needs:** Large, high-contrast typography; distinct, color-coded buttons (e.g., green for Serve, red for No-show) with large click targets; simple service dropdown filters to keep her dashboard clutter-free.

## 4. Research

### 4.1 Existing practice through observation
- Paper queue tickets and manual entry logs: Citizens receive physical paper tickets at the entrance guard station upon arrival, which are recorded manually or on a basic single-purpose printer.
- Overhead audio announcements: Counter staff rely on loudspeakers or calling out numbers manually to notify the room when a ticket is ready for processing.
- Lobby confinement and counter interruptions: Applicants are forced to remain seated or standing in a crowded, noisy lobby for hours. Fearing they will miss their turn, citizens frequently approach counter officers like Donna to ask for queue updates, interrupting document processing.

## 5. Functional Requirements

Priority: **Must** = needed for the Week 2 prototype, **Should** = planned for later weeks, **Could** = if time allows.

| ID | Requirement | Priority | Profile | Acceptance criteria |
|----|-------------|----------|---------|---------------------|
| FR-01 |Citizens shall be able to join the queue by submitting their name, email, and selected service. | Must | Applicant | Submitting valid inputs adds a ticket with status waiting and redirects to /queue/<ticket_id> with a success message.
| FR-02 | Citizens shall be able to check their ticket status, ticket number, service type, approximate waiting time, and position in line | Must | Applicant |Opening /queue/<ticket_id> displays ticket number prominently, status badge (waiting, called), and count of people ahead |
| FR-03 | Citizens shall be able to cancel or leave the queue if they are no longer available. | Must | Staff | Clicking "Leave the queue" sends a POST request setting ticket status to no-show and redirects home with a confirmation flash message |
| FR-04 | Staff shall be able to filter the queue list by a specific service. | Must | Staff | Selecting a service from the filter dropdown updates the staff table to display only waiting and called tickets for that service. |
| FR-05 | Staff shall be able to call the next waiting applicant in line. | Must | Staff | Clicking "Call next" updates the status of the first waiting ticket to |
| FR-06 | Staff shall be able to mark an applicant as served or as a no-show to update their status in the queue.| Must | Staff, Customer | Clicking "Serve" or "No-show" issues a POST request that updates ticket status to served or no-show and removes them from the active waiting list. |

## 6. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | **Usability & Speed:** Applicants can complete and submit the join queue form in under 30 seconds on a phone; staff can execute state changes (Call, Serve, No-show) in a single click on desktop |
| NFR-02 | **Accessibility & Readability:** Mobile interactive controls feature minimum 44 × 44 px touch targets for single-thumb use; staff dashboard uses high-contrast typography to support low-vision readability. Along with an option to have the application's language options (English, Tagalog, Cebuano, Arabic for the muslim population) |
| NFR-03 | **Performance:** Pages load in under 2 seconds on spotty mobile data in the lobby; live status auto-polling consumes minimal bandwidth via lightweight JSON updates.|
| NFR-04 | **Privacy:** The public /queue/<ticket_id> page displays only ticket numbers, service name, status, and position ahead without exposing full personal email addresses or confidential details. |
| NFR-05 | **Portability:** Runs on any modern browser with no installation. |

## 7. Scope

**In scope (course project):**
- Flask web app with Jinja2 templates
- In-memory Python data structures for queue tickets and services
- Core three-screen workflow: Join Queue form with server-side validation, "My Place" ticket status, and Staff Dashboard.

**Out of scope (future work):**
- Real SMS or Messenger notifications
- Direct integration with PhilSys biometric hardware or central government databases.
- Staff login, user authentication, and permission management.
- Multi-agency synchronization and offline local caching.

## 8. Data Model (initial)

**Service:** `id`, `name`

**Ticket (order):** `number`, `name`, `phone`, `service_id`, `status`

**Status values:** `waiting`, `called`, `served`, `no show`, `cancelled`

## 9. Success Measures

- Citizen Visibility & Autonomy: Applicants can join the queue in under 30 seconds and track their real-time position and status on "My place" without needing to refresh the page or interrupt counter officers.
- Staff Speed & Accuracy: Agency counter staff can filter waiting lists by service and execute status actions (Call Next, Serve, No-show) with a single click on the dashboard without misclicks or system errors.
- Accessibility & Mobile Responsiveness: The application scores 90 or higher on Chrome Lighthouse accessibility checks, passes keyboard navigation testing, and renders seamlessly on phone screens.

## 10. Risks

| Risk | Mitigation |
|------|------------|
|Counter officers find the digital dashboard difficult or slower than paper tickets and revert to vocal callouts. | Design a clutter-free UI with high-contrast, large text, single-click POST actions ("Call Next", "Serve"), and test usability with real counter staff. |
| Unreliable lobby internet connectivity | Keep web pages lightweight with small payloads and list full offline functionality as a future feature.|
| Estimated ready times are inaccurate | Display current line position based on active ticket counts ahead and refine timing calculations using real operational data later.|
| Customer data privacy | Omit personal contact information from public ticket pages, displaying only ticket numbers, services, and queue positions (NFR-04). |

## 11. Work Plan

| Week | Deliverable |
|------|-------------|
| 1 | Proposal, user profiles (James & Donna), research notes, and initial requirements (FR-01 to FR-06).|
| 2 | Initial Flask application environment setup and starter queue routing. |
| 3+ | QueuExpress first working interface: Join Queue form with server-side validation, My Place auto-refresh status page, Staff Dashboard with POST actions, user personas, wireframes, accessibility audit, and usability testing.|