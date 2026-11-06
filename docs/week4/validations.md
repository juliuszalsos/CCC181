# Part 10: Validation in Three Layers

| Rule | Layer | How I tested it | What happened |
| :--- | :--- | :--- | :--- |
| Email format required | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=Alex" -d "email=not-an-email" -d "service_id=1"` | `HTTP/1.1 400 BAD REQUEST`, 0 rows added |
| Name length limit | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=VeryLongName..." -d "email=a@b.com" -d "service_id=1"` | `HTTP/1.1 400 BAD REQUEST`, 0 rows added |
| Active service required | Flask | `curl.exe -i -X POST http://127.0.0.1:5000/join -d "name=Alex" -d "email=a@b.com" -d "service_id=999"` | `HTTP/1.1 400 BAD REQUEST`, 0 rows added |
| Foreign Key reference | Database | `INSERT INTO tickets (user_id, service_id) VALUES (1, 999);` in `psql` | `ERROR: insert or update on table "tickets" violates foreign key constraint "tickets_service_id_fkey"` |
| Unique constraint | Database | `INSERT INTO users (name, email) VALUES ('Copy', 'existing@domain.com');` in `psql` | `ERROR: duplicate key value violates unique constraint "users_email_key"` |
| Check constraint | Database | `UPDATE tickets SET status = 'lost' WHERE id = 1;` in `psql` | `ERROR: new row for relation "tickets" violates check constraint "tickets_status_check"` |
| Not Null constraint | Database | `INSERT INTO users (name, email) VALUES (NULL, 'nullname@domain.com');` in `psql` | `ERROR: null value in column "name" of relation "users" violates not-null constraint` |
| Restrict constraint | Database | `DELETE FROM services WHERE id = 1;` in `psql` | `ERROR: update or delete on table "services" violates foreign key constraint "tickets_service_id_fkey" on table "tickets"` |

## SQL Safety Check
Executed `git grep -nE "f[\"'].*(SELECT|INSERT|UPDATE|DELETE)" -- "*.py"` — returned 0 matches, confirming all database queries use SQLAlchemy parameter binding without raw f-string interpolation.