# QueuExpress requirements

**Setting:** Philippine Statistics Authority (PSA) provincial office in Iligan City, operating Mondays to Fridays from 8:00 AM to 5:00 PM
**People who wait:** Working parents and citizens visiting the agency for civil registry documents and PhilSys National ID applications (e.g., James Marthurin)
**People who serve:** Senior agency counter officers handling document verification and biometric capture (e.g., Donna Magsukul)

**Problem statement:** A working parent visiting the PSA office on limited free time needs a way to join the queue digitally and track their ticket status and position in real time from their phone because they risk missing voice announcements, losing their turn, or wasting a rare day off whenever they step away from the crowded, noisy lobby to care for their child

| ID | Requirement | Priority | Stores Data | Status  |
|----|-------------|----------|---------|---------------------|
| FR-01 | Citizens can join the queue by submitting their name, email, and selected service. | Must | **Yes** | Built (Week 3) |
| FR-02 | Citizens can check their ticket status, ticket number, service type, approximate waiting time, and position in line. | Must | **Yes** | Built (Week 3) |
| FR-03 | Citizens can cancel or leave the queue if they are no longer available. | Must | **Yes** | Built (Week 3) |
| FR-04 | Staff can filter the queue list by a specific service. | Must | **Yes** | Built (Week 3) |
| FR-05 | Staff can call the next waiting applicant in line. | Must | **Yes** | Built (Week 3) |
| FR-06 | Staff can mark an applicant as served or as a no-show to update their status in the queue. | Must | **Yes** | Built (Week 3) |
| FR-07 | Staff can deactivate or reactivate a service to control public availability. | Must | **Yes** | Later |
| FR-08 ★ | A senior citizen, PWD, or pregnant applicant can select a priority lane when joining the queue. | Should | **Yes** | Later |
| FR-09 | A staff member can save high-contrast and enlarged font display settings to their account profile to reduce desk eye strain. | Could | **Yes** | Later |
| FR-10 ★ | A citizen can specify the number of document copies requested (1 to 5 copies) when joining the queue for civil registry services. | Should | **Yes** | Later |
| FR-11 ★ | A staff member can attach a missing requirement remark (e.g., "Missing valid ID") when marking a ticket as no-show. | Should | **Yes** | Later |

| ID | Requirement | Category | Priority |
|----|-------------| ---------- | ----------- |
| NFR-01 | Applicants can complete and submit the join queue form in under 30 seconds on a phone; staff can execute state changes (Call, Serve, No-show) in a single click on desktop | Usability | Should |
| NFR-02 | Mobile interactive controls feature minimum 44 × 44 px touch targets for single-thumb use; staff dashboard uses high-contrast typography to support low-vision readability. Along with an option to have the application's language options (English, Tagalog, Cebuano, Arabic for the muslim population) | Accessibility | Should |
| NFR-03 | Pages load in under 2 seconds on spotty mobile data in the lobby; live status auto-polling consumes minimal bandwidth via lightweight JSON updates.| Performance | Should |
| NFR-04 | The public /queue/<ticket_id> page displays only ticket numbers, service name, status, and position ahead without exposing full personal email addresses or confidential details. | Privacy | Must |
| NFR-05 | Runs on any modern browser with no installation. | Portability | Must |
| NFR-6 | No active or historical ticket data is lost when the Flask app or PostgreSQL database container restarts. | Reliability | Must |

**MVP:** FR-01, FR-02, FR-03, FR-04, FR-05, FR-06, FR-07, NFR-01, NFR-02, NFR-03, NFR-05, NFR-06
*Why this is the smallest version:* This core set provides the minimum end-to-end functionality required for citizens to digitally join, monitor, and leave the queue on mobile, while giving counter staff full control to filter, call, serve, and manage service availability. Without these fundamental capabilities and database persistence (NFR-01), the app cannot solve lobby crowding or maintain queue state across server restarts.
**Out of Scope:**
1. **SMS and Messenger Notifications:** We will not implement automated SMS or messaging alerts this semester. Applicants track their live queue position directly through light-weight browser auto-polling on the "My place" page (`/queue/<ticket_id>`), avoiding third-party gateway costs and cell carrier reliance.
2. **PhilSys Biometric Hardware & Central Database Integration:** QueuExpress will not interface directly with physical biometric capture devices or central PSA civil registry databases. The app operates strictly as an independent queue management system to keep scope achievable and focused on lobby workflow.

| Who | What they said | What I changed |
|-----|----------------|------------------|
| Jan Mhar De Chavez | Priority lanes should be added to cater for the people with disabilities, pregnant, senior citizens, or is with child | Added FR-08 |