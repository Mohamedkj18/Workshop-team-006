# Lazy Mail – API Gateway

This is the central API Gateway for the Lazy Mail application. It serves as the unified entry point for all frontend requests and routes them to the appropriate microservices.

---

## 🚀 Features

- FastAPI-based lightweight gateway
- Routes all `/api/...` calls to backend services
- Handles CORS for frontend integration
- Uses `httpx` for async request forwarding
- Organized per-service routers

---

## 🧱 Directory Structure

```
api-gateway/
├── main.py              # FastAPI app entry point
├── requirements.txt     # Python dependencies
├── Dockerfile           # For containerization
├── .env                 # Optional env config
├── routers/             # Route handlers for services
│   ├── ai.py
│   ├── auth.py
│   ├── drafts.py
│   ├── emails.py
│   └── users.py
```

---

## 🛠️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the gateway locally

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Access from frontend

```http
GET http://localhost:8000/api/emails/inbox
POST http://localhost:8000/api/ai/generate-reply
```

---

## 🐳 Docker

To build and run with Docker:

```bash
docker build -t api-gateway .
docker run -p 8000:8000 api-gateway
```

---

## 🧠 Microservices Connected

| Service        | Routed Prefix | Example Endpoint              |
| -------------- | ------------- | ----------------------------- |
| AI Service     | `/api/ai`     | `POST /api/ai/generate-reply` |
| Auth Service   | `/api/auth`   | `POST /api/auth/login`        |
| Email Service  | `/api/emails` | `GET /api/emails/inbox`       |
| Drafts Service | `/api/drafts` | `GET /api/drafts`             |
| User Service   | `/api/users`  | `GET /api/users/{user_id}`    |

---

## ✅ Status

This gateway only provides the API of the routers.
