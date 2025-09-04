# Email AI Reply Automation System - Team 006

A sophisticated AI-powered email management system built with a microservices architecture. This system automates email reply generation, learns user writing styles, and provides comprehensive email management capabilities through an intuitive web interface.

## 🌟 Overview

This project implements a scalable email automation platform that combines artificial intelligence with user-centric design to streamline email communication. The system learns from user behavior, generates contextually appropriate responses, and provides a full-featured email client interface.

## 🏗️ Architecture

The system follows a microservices architecture pattern with the following components:

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │◄──►│   API Gateway   │
│   (React/Vite)  │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Service  │    │   AI Service    │    │  Email Service  │
│   (FastAPI)     │    │   (FastAPI)     │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Drafts Service  │    │User-Style Svc   │    │   Databases     │
│   (FastAPI)     │    │   (FastAPI)     │    │ MongoDB + PgSQL │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Key Features

### 🤖 AI-Powered Email Generation

- **Smart Reply Generation**: Context-aware email responses using OpenAI GPT models
- **Style Learning**: Learns individual user writing patterns and preferences
- **Personalization**: Adapts responses based on user's historical email behavior

### 📧 Complete Email Management

- **Inbox Management**: Full email client functionality with Gmail API integration
- **Draft System**: Create, edit, and manage email drafts
- **Email Organization**: Sent, starred, and trash folder management
- **Real-time Updates**: Live email synchronization and notifications

### 🎨 Modern User Interface

- **Responsive Design**: Mobile-first approach with modern UI components
- **Intuitive Navigation**: Clean sidebar navigation with contextual actions
- **Interactive Components**: Compose popups, reply interfaces, and email threading
- **Real-time Chat**: GPT-powered chat interface for email assistance

### 🔐 Authentication & Security

- **Google OAuth Integration**: Secure login with Google accounts
- **JWT Token Management**: Secure session handling and API authentication
- **User Profile Management**: Comprehensive user data and preferences

## 🛠️ Technology Stack

### Frontend

- **React 19** with modern hooks and context
- **Vite** for fast development and building
- **React Router** for navigation
- **Axios** for API communication
- **Lucide React** for consistent iconography

### Backend Services

- **FastAPI** for all microservices
- **Python 3.10+** runtime environment
- **Uvicorn** ASGI server
- **Pydantic** for data validation
- **HTTPx** for inter-service communication

### AI & Machine Learning

- **OpenAI GPT Models** for text generation
- **Custom Style Learning** algorithms
- **Email Classification** systems
- **Sentiment Analysis** for context understanding

### Databases

- **MongoDB** for user data, emails, and drafts
- **PostgreSQL** for user style profiles and learning data
- **Redis** (planned) for caching and session storage

### Infrastructure

- **Docker & Docker Compose** for containerization
- **Nginx** for frontend serving and reverse proxy
- **Background Schedulers** for automated tasks

## 📁 Project Structure

```
Workshop-team-006/
├── microservices/
│   ├── api-gateway/           # Central API routing and request handling
│   │   ├── main.py           # FastAPI application entry point
│   │   ├── routers/          # Route handlers for different domains
│   │   │   ├── ai.py         # AI service proxy routes
│   │   │   ├── auth.py       # Authentication routes
│   │   │   ├── drafts.py     # Draft management routes
│   │   │   ├── emails.py     # Email handling routes
│   │   │   ├── style.py      # User style service routes
│   │   │   └── users.py      # User management routes
│   │   └── models/           # Pydantic models for request/response
│   │
│   ├── ai-service/           # AI-powered email generation
│   │   ├── main.py           # Service entry point
│   │   ├── routers/          # AI-specific route handlers
│   │   ├── services/         # Core AI business logic
│   │   ├── utils/            # AI utilities and helpers
│   │   └── models/           # AI data models
│   │
│   ├── user-service/         # User authentication and management
│   │   ├── main.py           # Service entry point
│   │   ├── routes/           # Authentication routes
│   │   ├── services/         # Auth business logic
│   │   ├── models/           # User data models
│   │   └── db/               # Database connection and operations
│   │
│   ├── email-service/        # Email operations and Gmail integration
│   │   ├── main.py           # Service entry point
│   │   ├── routes/           # Email-specific routes
│   │   ├── services/         # Email business logic
│   │   ├── models/           # Email data models
│   │   └── db/               # Email database operations
│   │
│   ├── drafts-service/       # Email draft management
│   │   ├── main.py           # Service entry point
│   │   ├── routes/           # Draft management routes
│   │   ├── models/           # Draft data models
│   │   ├── utils/            # Draft utilities
│   │   └── config/           # Service configuration
│   │
│   ├── user-style-service/   # User writing style learning
│   │   ├── main.py           # Service entry point
│   │   ├── routers/          # Style-related routes
│   │   ├── services/         # Style learning algorithms
│   │   ├── db/               # PostgreSQL models and operations
│   │   └── utils/            # Style analysis utilities
│   │
│   └── frontend service/     # React web application
│       ├── src/
│       │   ├── components/   # Reusable UI components
│       │   ├── pages/        # Application pages/views
│       │   ├── context/      # React context providers
│       │   ├── api/          # API communication layer
│       │   ├── routes/       # Route protection and navigation
│       │   └── layout/       # Application layout components
│       ├── public/           # Static assets
│       └── package.json      # Frontend dependencies
│
├── docker-compose.yml        # Multi-container application orchestration
└── README.md                # This documentation file
```

## 🚀 Getting Started

### Prerequisites

Before running the application, ensure you have the following installed:

- **Docker** (version 20.0+) and **Docker Compose** (version 2.0+)
- **Node.js** (version 18+) and **npm** for local frontend development
- **Python** (version 3.10+) for local backend development

### Environment Configuration

**⚠️ Important: `.env` File Required**

This application requires a `.env` file containing sensitive configuration data including:

- OpenAI API keys
- Database connection strings
- OAuth client secrets
- Service URLs and ports

**The `.env` file will be provided separately via email to the instructors** as it contains sensitive information that should not be committed to version control.

Place the provided `.env` file in the `microservices/` directory before running the application.

### Installation & Setup

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd Workshop-team-006
   ```

2. **Add Environment File**

   ```bash
   # Place the provided .env file in the microservices directory
   cp path/to/provided/.env microservices/.env
   ```

3. **Start the Application**

   ```bash
   cd microservices
   docker-compose up --build
   ```

4. **Verify Installation**
   - Frontend: http://localhost:5173
   - API Gateway: http://localhost:8000
   - Individual services on their respective ports

### Development Mode

For local development with hot reloading:

**Backend Services (each in separate terminal):**

```bash
# API Gateway
cd microservices/api-gateway
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# AI Service
cd microservices/ai-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# Other services follow similar pattern...
```

**Frontend:**

```bash
cd microservices/frontend\ service
npm install
npm run dev
```

## 🔧 Service Details

### API Gateway (Port 8000)

**Purpose**: Central routing hub that coordinates requests between frontend and backend services.

**Key Features**:

- Request routing and load balancing
- CORS configuration for frontend communication
- Health check endpoints
- Centralized error handling

**Endpoints**: `/api/*` - All API routes are prefixed and routed to appropriate services

### AI Service (Port 8001)

**Purpose**: Handles all AI-powered features including email generation and content analysis.

**Key Features**:

- OpenAI GPT integration for email generation
- Context-aware response creation
- Email content analysis and classification
- Custom prompt engineering for different email types

**Main Endpoints**:

- `POST /generate-reply` - Generate AI email responses
- `POST /analyze-email` - Analyze email content and sentiment

### User Service (Port 8004)

**Purpose**: Manages user authentication, profiles, and session handling.

**Key Features**:

- Google OAuth 2.0 integration
- JWT token generation and validation
- User profile management
- Secure session handling

**Main Endpoints**:

- `POST /auth/login` - User authentication
- `GET /auth/profile` - User profile retrieval
- `POST /auth/logout` - Session termination

### Email Service (Port 8003)

**Purpose**: Handles email operations, Gmail API integration, and email data management.

**Key Features**:

- Gmail API integration for email fetching
- Email sending and receiving
- Email metadata management
- Attachment handling

**Main Endpoints**:

- `GET /emails` - Retrieve user emails
- `POST /emails/send` - Send email messages
- `GET /emails/{id}` - Get specific email details

### Drafts Service (Port 8002)

**Purpose**: Manages email draft creation, editing, and storage.

**Key Features**:

- Draft creation and modification
- Auto-save functionality
- Draft categorization and organization
- Version control for draft changes

**Main Endpoints**:

- `GET /drafts` - Retrieve user drafts
- `POST /drafts` - Create new draft
- `PUT /drafts/{id}` - Update existing draft
- `DELETE /drafts/{id}` - Delete draft

### User-Style Service (Port 8010)

**Purpose**: Learns and analyzes user writing patterns to personalize AI responses.

**Key Features**:

- Writing style analysis and learning
- User behavior pattern recognition
- Style-based response customization
- Continuous learning from user interactions

**Main Endpoints**:

- `POST /style/learn` - Add user writing samples
- `GET /style/profile` - Get user style profile
- `POST /style/apply` - Apply learned style to content

## 🗄️ Database Configuration

### MongoDB (Port 27017)

**Usage**: Primary database for user data, emails, and application state.

**Collections**:

- `users` - User profiles and authentication data
- `emails` - Email messages and metadata
- `drafts` - Email drafts and versions
- `sessions` - User session data

### PostgreSQL (Port 5543)

**Usage**: Specialized database for user style learning and analytics.

**Tables**:

- `user_styles` - User writing style profiles
- `email_features` - Extracted email features for learning
- `style_clusters` - Grouped writing patterns
- `learning_buffer` - Temporary data for style analysis

## 🌐 API Documentation

### Authentication Flow

```
1. User initiates Google OAuth → User Service
2. OAuth callback processed → JWT token generated
3. Token used for all subsequent API calls
4. Token validation on each request
```

### Email Generation Flow

```
1. User composes email → Frontend
2. Request routed through API Gateway
3. AI Service generates response using GPT
4. User-Style Service personalizes response
5. Final response returned to user
```

### Style Learning Flow

```
1. User sends/edits emails → Email Service
2. Email content analyzed → User-Style Service
3. Features extracted and stored → PostgreSQL
4. Style profile updated → Background scheduler
5. Improved personalization for future responses
```

## 🔒 Security Considerations

- **Environment Variables**: Sensitive data stored in `.env` file (provided separately)
- **OAuth Integration**: Secure Google authentication flow
- **JWT Tokens**: Stateless authentication with expiration
- **CORS Configuration**: Restricted origins in production
- **Input Validation**: Pydantic models for all API inputs
- **Database Security**: Connection strings and credentials protected

## 🚦 Health Checks & Monitoring

The application includes comprehensive health checking:

- **Database Health**: MongoDB and PostgreSQL connection status
- **Service Health**: Individual microservice status endpoints
- **API Gateway Health**: Overall system status at `/health`
- **Container Health**: Docker health checks for all services

## 🧪 Testing

### Running Tests

```bash
# Backend tests
cd microservices/<service-name>
python -m pytest tests/

# Frontend tests
cd microservices/frontend\ service
npm test
```

### Test Coverage

- Unit tests for core business logic
- Integration tests for API endpoints
- End-to-end tests for critical user flows
- Database operation tests

## 🔄 Deployment

### Production Deployment

1. **Environment Setup**: Configure production `.env` with appropriate values
2. **Database Setup**: Set up MongoDB and PostgreSQL instances
3. **Container Registry**: Push images to container registry
4. **Orchestration**: Deploy using Docker Compose or Kubernetes
5. **SSL/TLS**: Configure HTTPS certificates
6. **Monitoring**: Set up logging and monitoring solutions

### Scaling Considerations

- **Horizontal Scaling**: Add more service instances behind load balancer
- **Database Scaling**: Implement read replicas and sharding
- **Caching**: Add Redis for session and response caching
- **CDN**: Use CDN for static frontend assets

## 🐛 Troubleshooting

### Common Issues

**Services Not Starting**:

- Verify `.env` file is present and properly configured
- Check Docker daemon is running
- Ensure ports are not already in use

**Database Connection Issues**:

- Verify database containers are healthy
- Check connection strings in environment variables
- Ensure proper network connectivity between services

**Authentication Problems**:

- Verify Google OAuth credentials are correct
- Check JWT token expiration settings
- Ensure proper CORS configuration

**AI Service Issues**:

- Verify OpenAI API key is valid and has sufficient credits
- Check API rate limits and quotas
- Monitor OpenAI API status

## 📈 Performance Optimization

- **Database Indexing**: Optimized queries with proper indexes
- **Caching Strategy**: Response caching for frequently accessed data
- **Connection Pooling**: Efficient database connection management
- **Async Processing**: Non-blocking operations for better throughput
- **Resource Monitoring**: Container resource limits and monitoring

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 📄 License

This project is part of an academic workshop on scalable AI systems. Please refer to your course materials for specific licensing terms.

## 👥 Team 006

This project was developed as part of the "Workshop on Scalable AI Systems" course.

---

**Note**: The `.env` file containing sensitive configuration data (API keys, database credentials, etc.) will be provided separately via email to the instructors. This file is required for the application to function properly and should be placed in the `microservices/` directory before running the application.

For any questions or issues, please contact the development team or refer to the course instructors.
