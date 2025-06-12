# Email AI Reply Automation System

An AI-powered email response system that automates the generation, editing, and management of email replies using OpenAI's GPT models. Built with a modular microservices architecture using FastAPI, React, and RabbitMQ.

## 🔧 Features

- ✉️ Compose and manage email drafts
- 🤖 Ask AI to generate context-aware replies
- 📤 Send, schedule, or save replies
- 🧠 Smart reply classification: AI-generated vs manually written
- 🔁 Microservices architecture for scalability and modularity

## 📁 Project Structure

```
.
├── frontend/              # React app for UI
│   └── ...
├── api-gateway/           # FastAPI service acting as entry point for frontend
│   └── main.py
├── ai-service/            # FastAPI service handling AI-based reply generation
│   └── main.py
├── docker-compose.yml     # Docker orchestration
├── .env                   # Environment variables
└── README.md              # You're here
```

## 🚀 Getting Started

### Prerequisites

- Docker + Docker Compose
- OpenAI API key
- Python 3.10+ (for local development)

### Running Locally (Dev Mode)

**AI Service:**

```bash
cd ai-service
uvicorn main:app --reload
```

**API Gateway:**

```bash
cd api-gateway
uvicorn main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm start
```

## 📬 Usage Flow

1. Open the Compose popup to write or reply to an email.
2. Click **Ask AI** to let the system generate a smart response.
3. Edit, approve, or delete the AI-generated reply.
4. Send or save the draft.

## 🌐 API Endpoints

### POST `/generate-reply`

Request:

```json
{
  "email_content": "Hi, can we reschedule our meeting to tomorrow at 2PM?"
}
```

Response:

```json
{
  "ai_reply": "Sure! Tomorrow at 2PM works perfectly. Let me know if anything changes."
}
```

### POST `/send`, `/drafts`, `/approve`, etc.

(See full Swagger docs via API Gateway)

## 📌 Roadmap

- [x] Ask AI to generate replies
- [x] Approve/edit AI drafts
- [x] Save and manage manual drafts
- [ ] Gmail API integration
- [ ] Multi-user support
- [ ] Smart thread summarization
