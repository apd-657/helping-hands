# 🤝 Helping Hands

> Connecting elderly people with caring young volunteers for daily assistance.

---

## 📁 Folder Structure

```
helping-hands/
├── backend/                    ← Python FastAPI server
│   ├── main.py                 ← App entry point (start here!)
│   ├── database.py             ← SQLite connection setup
│   ├── models.py               ← Database table definitions
│   ├── schemas.py              ← Data validation (Pydantic)
│   ├── auth.py                 ← JWT login & password hashing
│   ├── seed_data.py            ← Populate DB with test data
│   ├── requirements.txt        ← Python dependencies
│   └── routers/
│       ├── users.py            ← /api/users/* endpoints
│       └── requests.py         ← /api/requests/* endpoints
│
└── frontend/                   ← HTML/CSS/JS (no build step!)
    ├── index.html              ← Home page
    ├── auth.html               ← Login & Register
    ├── dashboard.html          ← User dashboard
    ├── request-help.html       ← Elder: create request
    ├── available-requests.html ← Volunteer: browse & accept
    ├── css/
    │   └── style.css           ← All styles
    └── js/
        └── api.js              ← All API calls + helpers
```

---

## 🚀 Quick Start (Local Development)

### Step 1 — Backend Setup

```bash
# Go to backend folder
cd helping-hands/backend

# Create a virtual environment (keeps packages isolated)
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install all packages
pip install -r requirements.txt

# Start the server
python main.py
```

✅ Backend is now running at: **http://localhost:8000**
📖 API docs (Swagger UI): **http://localhost:8000/docs**

### Step 2 — Seed Sample Data (Optional)

```bash
# While in the backend folder with venv active:
python seed_data.py
```

This creates 4 test accounts and sample requests:
| Name | Email | Password | Role |
|------|-------|----------|------|
| Margaret Johnson | margaret@example.com | password123 | Elder |
| Robert Williams | robert@example.com | password123 | Elder |
| Alex Chen | alex@example.com | password123 | Volunteer |
| Priya Sharma | priya@example.com | password123 | Volunteer |

### Step 3 — Frontend Setup

No build step needed! Just open the HTML files.

**Option A — VS Code Live Server (recommended):**
1. Install the "Live Server" extension in VS Code
2. Right-click `frontend/index.html` → "Open with Live Server"

**Option B — Python simple server:**
```bash
cd helping-hands/frontend
python -m http.server 5500
# Open: http://localhost:5500
```

**Option C — Just open the file:**
Double-click `frontend/index.html` in your file manager.
*(Note: Some browsers block fetch() from file:// — use Live Server if you see CORS errors)*

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users/register` | Create new account | ❌ |
| POST | `/api/users/login` | Login, get JWT token | ❌ |
| GET | `/api/users/me` | Get your profile | ✅ |
| GET | `/api/users/volunteers` | List all volunteers | ✅ |

**Register example:**
```json
POST /api/users/register
{
  "name": "Margaret Johnson",
  "email": "margaret@example.com",
  "password": "password123",
  "age": 75,
  "role": "elder",
  "contact": "555-0101",
  "location": "Downtown, Springfield"
}
```

**Login example:**
```json
POST /api/users/login
{
  "email": "margaret@example.com",
  "password": "password123"
}
```
Returns: `{ "access_token": "eyJ...", "token_type": "bearer", "role": "elder", ... }`

Use the token in all subsequent requests:
```
Authorization: Bearer eyJ...
```

---

### Help Requests

| Method | Endpoint | Description | Role |
|--------|----------|-------------|------|
| POST | `/api/requests/` | Create help request | Elder |
| GET | `/api/requests/` | List all requests (filter by status/category) | Any |
| GET | `/api/requests/my` | My own requests | Any |
| GET | `/api/requests/{id}` | Get single request | Any |
| PATCH | `/api/requests/{id}/accept` | Accept a request | Volunteer |
| PATCH | `/api/requests/{id}/complete` | Mark as complete | Elder/Volunteer |
| DELETE | `/api/requests/{id}` | Delete pending request | Elder (owner) |

**Create request example:**
```json
POST /api/requests/
{
  "title": "Grocery Shopping Needed",
  "description": "Need milk, bread, and vegetables from SuperMart",
  "category": "grocery",
  "location": "123 Maple St, Springfield"
}
```

**Filter requests:**
```
GET /api/requests/?status=pending&category=grocery
```

---

### Messages (Chat)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/requests/{id}/messages` | Send message |
| GET | `/api/requests/{id}/messages` | Get all messages |

---

## 🗄️ Database Schema

```sql
-- Users table
CREATE TABLE users (
    id               INTEGER PRIMARY KEY,
    name             TEXT NOT NULL,
    email            TEXT UNIQUE NOT NULL,
    hashed_password  TEXT NOT NULL,
    age              INTEGER,
    role             TEXT NOT NULL,    -- 'elder' or 'volunteer'
    contact          TEXT,
    location         TEXT,
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Requests table
CREATE TABLE requests (
    id               INTEGER PRIMARY KEY,
    title            TEXT NOT NULL,
    description      TEXT NOT NULL,
    category         TEXT NOT NULL,    -- 'grocery','hospital','medicine','other'
    location         TEXT NOT NULL,
    status           TEXT DEFAULT 'pending',  -- 'pending','accepted','completed'
    elder_id         INTEGER REFERENCES users(id),
    volunteer_id     INTEGER REFERENCES users(id),  -- NULL until accepted
    created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at       DATETIME
);

-- Messages table (chat)
CREATE TABLE messages (
    id         INTEGER PRIMARY KEY,
    request_id INTEGER REFERENCES requests(id),
    sender_id  INTEGER REFERENCES users(id),
    content    TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🌐 Deployment (Free)

### Backend → Render.com

1. Push your `backend/` folder to a GitHub repository
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Python 3
5. Click **Deploy**

After deployment, copy your Render URL (e.g. `https://helping-hands.onrender.com`)

### Frontend → Netlify.com

1. Update `API_BASE` in `frontend/js/api.js`:
   ```js
   const API_BASE = "https://helping-hands.onrender.com"; // Your Render URL
   ```
2. Go to [netlify.com](https://netlify.com) → Add new site → Deploy manually
3. Drag and drop the `frontend/` folder
4. Done! ✅

### Backend → Railway.app (Alternative)

1. Install Railway CLI: `npm install -g @railway/cli`
2. `cd backend && railway login && railway init && railway up`
3. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## 🔒 Security Notes (for Production)

1. **Change the SECRET_KEY** in `auth.py` — use a long random string
2. **Update CORS** in `main.py` — replace `"*"` with your Netlify URL
3. **Use environment variables** for secrets:
   ```python
   import os
   SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-dev-key")
   ```
4. **Use PostgreSQL** instead of SQLite for production (Render provides free PostgreSQL)

---

## 🧪 Testing the API

Visit **http://localhost:8000/docs** for interactive Swagger UI — you can test every endpoint directly in the browser without writing any code!

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Make sure virtual environment is activated |
| CORS error in browser | Ensure backend is running on port 8000 |
| `401 Unauthorized` | Token expired — log in again |
| Database errors | Delete `helping_hands.db` and restart to reset |
| Port 8000 in use | Run `uvicorn main:app --port 8001` |
