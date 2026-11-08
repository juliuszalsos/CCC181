11a. The Restart Test

1. Create at least five tickets across at least two services. Call one, serve one, and let one person leave.

2. 📷 The staff dashboard, and the result of SELECT id, status, service_id, created_at FROM tickets ORDER BY id; in psql.
**Before Restart:**
* Staff Dashboard:
  ![Staff Dashboard](screenshots/Staff%20dashboard.png)
* SQL Query Output:
  ![SQL Return Text](screenshots/SQL%20return%20text.png)

3. Stop Flask with Ctrl+C. Run docker compose down. Run docker compose ps and see that nothing is running.

4. Run docker compose up -d, wait until docker compose ps says healthy, then start Flask again.

5. 📷 The same dashboard and the same SQL query. Every ticket, status and time must be exactly as before.
**After Restart:**
* Staff Dashboard (Post-restart):
  ![After Restart Dashboard](screenshots/After%20restart.png)
* SQL Query Output (Post-restart):
  ![Proof of Database Restart](screenshots/Proof%20of%20database%20restart.png)

11b. Rebuild from scratch
after performing 
docker compose down -v
docker compose up -d
flask --app app db upgrade
flask --app app seed

the web application was refreshed and the people in the queue disappeared and the app can take new tickets to process the new queue to be added.

11c. 