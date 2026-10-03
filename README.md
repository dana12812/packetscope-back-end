# PacketScope — Back End

**The FastAPI + PostgreSQL API behind PacketScope.**

This repository is the **back end** for PacketScope, a network packet-capture analysis app. It handles authentication and user roles, full CRUD for captures, notes and tags, an admin API with an activity log, and parses uploaded `.pcap` / `.pcapng` files with [Scapy](https://scapy.net/) into a compact traffic summary.

It runs on **[Render](https://render.com)** with its PostgreSQL database hosted on **[Neon](https://neon.tech)** — see [Deployment](#deployment).

🖥️ **Front-end repo (full project details, screenshots and planning):** [packetscope-front-end](https://github.com/dana12812/packetscope-front-end)

🌐 **Live app:** [https://packetscope-psi.vercel.app](https://packetscope-psi.vercel.app)

⚙️ **Live API:** [https://packetscope-api.onrender.com](https://packetscope-api.onrender.com/health) — interactive docs at [/docs](https://packetscope-api.onrender.com/docs)

---

## Table of contents

1. [Data model (ERD)](#data-model-erd)
2. [API endpoints](#api-endpoints)
3. [Packet parsing](#packet-parsing)
4. [Authentication & authorization](#authentication--authorization)
5. [Getting started](#getting-started)
6. [Deployment](#deployment)
7. [Admin accounts](#admin-accounts)
8. [Technologies used](#technologies-used)
---

## Data model (ERD)

![PacketScope ERD](docs/PacketScope-ERD.jpg)

Interactive version: [PacketScope on DrawSQL](https://drawsql.app/teams/dana-alsaleh/diagrams/packetscope)

| Table | Purpose | Key relationships |
|---|---|---|
| `users` | Accounts, with a `role` of `user` or `admin` | Owns captures, annotations and tags |
| `captures` | An uploaded capture and its parsed summary (JSON) | Belongs to a user; has many annotations |
| `annotations` | Notes on a capture | Belongs to a capture and to its author |
| `tags` | Color-coded labels | Belongs to a user |
| `capture_tags` | Join table | Links captures ↔ tags (many-to-many) |
| `activities` | Audit log of user actions | Stores the actor's id and username, with no foreign key, so history survives when a user or capture is deleted |

## API endpoints

All routes are prefixed with `/api`. Every route except register and login requires a JWT in an `Authorization: Bearer <token>` header.

### Auth

| Method | Route | Description |
|---|---|---|
| POST | `/api/register` | Create an account and receive a JWT |
| POST | `/api/login` | Sign in and receive a JWT |
| GET | `/api/current_user` | The signed-in user (used to verify a saved session) |

### Captures

| Method | Route | Description |
|---|---|---|
| GET | `/api/captures` | List the current user's captures |
| POST | `/api/captures` | Upload and analyze a capture file (multipart, max 5 MB) |
| GET | `/api/captures/{capture_id}` | One capture with its summary — owner, or any capture for admins |
| PUT | `/api/captures/{capture_id}` | Rename a capture and/or set its tags (`filename`, `tag_ids`) — owner only |
| DELETE | `/api/captures/{capture_id}` | Delete a capture and its notes — owner only |

### Notes (annotations)

| Method | Route | Description |
|---|---|---|
| GET | `/api/captures/{capture_id}/annotations` | List notes on a capture, with author name and role |
| POST | `/api/captures/{capture_id}/annotations` | Add a note — capture owner or admin |
| PUT | `/api/annotations/{annotation_id}` | Edit a note — author only |
| DELETE | `/api/annotations/{annotation_id}` | Delete a note — author only |

### Tags

| Method | Route | Description |
|---|---|---|
| GET | `/api/tags` | List the current user's tags |
| POST | `/api/tags` | Create a tag (`name`, `color`) |
| PUT | `/api/tags/{tag_id}` | Rename or recolor a tag |
| DELETE | `/api/tags/{tag_id}` | Delete a tag (it is removed from every capture) |

### Admin (admin role required)

| Method | Route | Description |
|---|---|---|
| GET | `/api/admin/users` | All users with capture count, note count and last activity |
| GET | `/api/admin/users/{user_id}` | One user with their captures |
| PATCH | `/api/admin/users/{user_id}` | Change a user's role (`user` / `admin`) |
| DELETE | `/api/admin/users/{user_id}` | Delete a user and their captures, notes and tags |
| GET | `/api/admin/activity` | Activity log, newest first (`?user_id=` and `?limit=` optional) |

Admins cannot delete their own account or remove their own admin role.

## Packet parsing

When a capture is uploaded, the back end:

1. **Checks the size** — files over 5 MB are rejected with a clear error.
2. **Reads** it with Scapy's `rdpcap`. If the file isn't a readable capture, it returns `400` with *"Could not read file as a .pcap capture"*.
3. **Summarizes** the traffic (`lib/pcap_parser.py`):
   - packet count and duration
   - protocol counts — TCP, UDP, ICMP, ARP and other
   - top source and destination IPs (IPv4 and IPv6)
   - top services by destination port (e.g. https, dns, ssh)
   - total bytes and min / average / max packet size
4. **Stores** the summary as JSON on the `captures` row, so pages load instantly without re-parsing.

## Authentication & authorization

- **Passwords** are hashed with bcrypt (passlib) — plaintext is never stored.
- **Sessions** use JWTs (PyJWT, HS256) that expire after one day. The token carries the user's id, username and role.
- **Authorization** — captures, notes and tags are filtered by the signed-in user. Admins can additionally read any capture and add notes to it, but only the owner can edit or delete a capture, and only the author can edit or delete a note.
- **Admin checks** read the role from the database on every request, not from the token, so a role change takes effect immediately.
- **Activity log** — sign-ups, sign-ins, uploads, renames, tag changes, deletions, notes and role changes are recorded for the admin page.

## Getting started

Requirements: Python 3.12, [pipenv](https://pipenv.pypa.io/) and PostgreSQL.

```bash
git clone https://github.com/dana12812/packetscope-back-end.git
cd packetscope-back-end
pipenv install
```

Copy `.env.example` to `.env` and fill in the values:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Long random string used to sign tokens |
| `CORS_ORIGINS` | Front-end URLs allowed to call the API, comma-separated (default `http://localhost:5173`) |
| `ADMIN_USERNAMES` | Optional — comma-separated usernames that become admin when they sign in |

Start the server — any missing tables are created automatically on startup:

```bash
pipenv run uvicorn main:app --reload
```

The API runs at `http://localhost:8000` (interactive docs at `/docs`).

Optional: `pipenv run python seed.py` fills a **local** database with test users, captures and tags. It **drops and recreates** every table, so never run it against the deployed database. To upgrade an older local database to roles and the activity log without losing data, run `pipenv run python migrate.py` — it is safe to run more than once.

## Deployment

| Part | Platform | Details |
|---|---|---|
| **API** | [Render](https://render.com) — Web Service (free) | `https://packetscope-api.onrender.com`, region Oregon, auto-deploys from `master` |
| **Database** | [Neon](https://neon.tech) — serverless PostgreSQL (free) | Region AWS US West 2 (Oregon), next to the API |
| **Front end** | [Vercel](https://vercel.com) | `https://packetscope-psi.vercel.app` — see the [front-end repo](https://github.com/dana12812/packetscope-front-end) |

**Render settings**

| Setting | Value |
|---|---|
| Runtime | Python 3 (version from `.python-version`) |
| Build command | `pip install -r requirements.txt` |
| Start command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

**Environment variables on Render**

| Variable | Value |
|---|---|
| `DATABASE_URL` | Neon connection string (`postgresql://…?sslmode=require`) |
| `JWT_SECRET` | A long random string, different from the local one |
| `CORS_ORIGINS` | `https://packetscope-psi.vercel.app,http://localhost:5173` |
| `ADMIN_USERNAMES` | Usernames that become admin when they sign in |

Notes:

- The tables are created automatically on the first start — `seed.py` is never run against the Neon database.
- Render's free tier sleeps after about 15 minutes without traffic; the first request afterwards takes up to a minute while it wakes up.
- Secrets live only in Render's environment settings, never in the repository.

## Admin accounts

There are three ways to make someone an admin:

1. **`ADMIN_USERNAMES`** (easiest when deployed) — sign up the account first, then add its username to this environment variable. It becomes admin the next time it signs in.
2. **From the app** — an existing admin opens **Admin → user → Make admin**.
3. **From the terminal** — `pipenv run python create_admin.py <username>` (add `--email` for a new account). The password is typed at a hidden prompt.

## Technologies used

| Category | Technologies |
|---|---|
| **Language** | Python 3.12 |
| **Framework** | FastAPI, Uvicorn |
| **ORM** | SQLAlchemy |
| **Validation** | Pydantic v2 |
| **Database** | PostgreSQL (psycopg2), hosted on [Neon](https://neon.tech) |
| **Auth** | JWT (PyJWT), bcrypt (passlib) |
| **Packet parsing** | Scapy |
| **Hosting** | [Render](https://render.com) (API), [Neon](https://neon.tech) (database) |



---

**Author:** Dana AlSaleh — [GitHub](https://github.com/dana12812)
