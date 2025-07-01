# 🤖 AI-Service

This microservice is responsible for generating AI-based email replies and learning user writing styles. It is part of a larger microservices-based AI email assistant system.

---

## 📌 Responsibilities

- **Generate automated replies** to incoming emails using OpenAI GPT.
- **Analyze past emails** to learn a user’s writing style, including tone, length, and complexity.
- **Respond to messages** from other services via HTTP and RabbitMQ.

---

## 🚀 Features

- Uses **OpenAI's GPT-4** for reply and tone analysis.
- Listens to **RabbitMQ** queue (`new-email`) for incoming email events.
- Exposes a **REST API endpoint** (`/learn-style`) for user style learning.
- Stores user tone preferences in a local JSON file (`user_tones.json`).

---

## 🛠 Technologies

- Python 3.10+
- OpenAI API
- FastAPI (for REST endpoint)
- Pika (RabbitMQ client)
- Docker

---

## 📁 File Structure

```
AI-service/
├── main.py              # Consumes email messages and handles Flask/FastAPI app
├── ai_utils.py          # Handles AI reply generation
├── style_learning.py    # Learns user tone from historical emails
├── user_tones.json      # Stores user style profile (tone, length, complexity)
├── requirements.txt     # Python dependencies
└── Dockerfile           # Container for deployment
```

---

## 🧪 How It Works

### 🔁 Email Reply Flow

1. `email-service` publishes a new email to RabbitMQ (`new-email` queue).
2. `AI-service` consumes the message.
3. It uses OpenAI GPT to generate a reply.
4. It sends the generated reply to `drafts-service` via a REST call.

### 🧠 Style Learning Flow

1. On user sign-up or import, another service can send a `POST` to `/learn-style` with past emails.
2. AI analyzes the emails and infers writing style.
3. It updates the user’s style profile in `user_tones.json`.

---

## ⚙️ Running Locally

### 1. Clone the repo and install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your OpenAI API key

Create a `.env` file or set environment variable:

```env
OPENAI_API_KEY=sk-...
```

### 3. Run the service

```bash
python main.py
```

Or if you’re using FastAPI:

```bash
uvicorn main:app --reload
```

---

## 🐳 Docker Usage

### Build the image

```bash
docker build -t ai-service .
```

### Run the container (in Docker network)

```bash
docker run --network my-network -e OPENAI_API_KEY=sk-... ai-service
```

---

## 🔌 Environment Variables

| Variable         | Required | Description            |
| ---------------- | -------- | ---------------------- |
| `OPENAI_API_KEY` | ✅       | Your OpenAI secret key |

---

## 📫 API Endpoints

### `POST /learn-style`

**Description**: Learns writing style based on past emails.

**Payload:**

```json
{
  "user_id": "1234",
  "emails": [
    { "body": "Thanks! I’ll check it out and get back to you." },
    { "body": "Sure, let’s do 3 PM tomorrow." }
  ]
}
```

**Response:**

```json
{
  "user_id": "1234",
  "inferred_tone": "friendly",
  "length": "short",
  "complexity": "simple"
}
```

---

## 📎 Related Services

- `email-service`: Provides new emails
- `drafts-service`: Stores generated replies
- `user-service`: (optional) Could replace local `user_tones.json`

---
