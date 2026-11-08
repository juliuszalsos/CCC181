# Schema Self-Review

### Entry 1: Dynamic Calculation vs. Stored State
* **Works well:** Queue position and estimated wait times are computed on-demand using `tickets.created_at` and `services.avg_minutes` rather than stored as fixed integer columns in the `tickets` table.
* **Problem:** Discovered while reviewing Question 3 (*Facts, not results*): Storing a static `position` column would force the system to perform heavy database updates across dozens of waiting rows every time someone leaves, cancels, or gets called.
* **Change:** Kept `position` and `wait_time` out of the database schema entirely. The application computes line position dynamically via SQL (`COUNT()` of tickets with status `waiting` and an earlier `created_at` timestamp).

---

### Entry 2: Preserving Audit History on Foreign Key Deletes
* **Works well:** Foreign keys on `tickets.user_id` and `tickets.service_id` guarantee that every queue ticket links directly to a valid citizen account and PSA service record.
* **Problem:** Discovered while reviewing Question 5 (*Deletes*): Using `ON DELETE CASCADE` on foreign key relations would mean deleting a service or user account would instantly delete all historical ticket logs associated with them, destroying daily counter reports needed by PSA staff.
* **Change:** Configured `ON DELETE RESTRICT` for both foreign keys. Instead of deleting obsolete services from the database, staff soft-deactivate them by setting `services.active = false` (FR-07), retaining full historical audit trails.

---

### Entry 3: Preventing Invalid Inputs at the Database Layer
* **Works well:** Explicit `CHECK` constraints on `copies_requested`, `status`, `avg_minutes`, and `role` act as a final guardrail against bad data reaching PostgreSQL.
* **Problem:** Discovered while reviewing Question 4 (*Bad data*): Relying solely on Flask form validation could allow invalid inputs—such as zero/negative document copy counts or illegal ticket status strings—if a request bypasses the frontend UI.
* **Change:** Added strict database constraints: `CHECK (copies_requested BETWEEN 1 AND 5)`, `CHECK (avg_minutes > 0)`, `CHECK (status IN ('waiting', 'called', 'served', 'no-show', 'left', 'cancelled'))`, and `CHECK (role IN ('visitor', 'staff'))`.

---

### Entry 4: Time-Zone Safety for Audit Logs
* **Works well:** All timestamp fields (`created_at`, `called_at`) are explicitly defined as `timestamptz`.
* **Problem:** Discovered while reviewing Question 6 (*Types*): Using plain `timestamp` without time zone information or storing dates as text strings would introduce timestamp ambiguity when filtering daily counter queues across server reboots or system migrations.
* **Change:** Standardized all date/time columns to PostgreSQL `timestamptz` with `DEFAULT now()`, ensuring precise time-zone-aware tracking for PSA Iligan City operations.