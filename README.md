# AgentArena - AI Agent Benchmarking Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-A+-brightgreen.svg)](ARCHITECTURE.md)

> **Enterprise-Grade AI Agent Evaluation Platform** - A comprehensive benchmarking solution for evaluating AI agents in realistic web environments, inspired by WebArena and designed for production use.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)

---

## 🌟 Overview

AgentArena is an enterprise-grade AI agent benchmarking platform that enables comprehensive evaluation of AI agents across complex, real-world scenarios. Built with modern technologies and following industry best practices, it provides isolated environments, robust evaluation metrics, and competitive leaderboards for advancing AI agent capabilities.

### Core Objectives

- **🎯 Comprehensive Evaluation**: Test AI agents across diverse web-based tasks with standardized metrics
- **🌐 Realistic Environments**: Provide isolated, reproducible testing environments using WebArena-inspired tasks
- **📊 Performance Analytics**: Advanced metrics, performance tracking, and comparative analysis
- **🏆 Competitive Benchmarking**: Public leaderboards and research-grade evaluation protocols
- **🔬 Research Foundation**: Support academic and industry research in AI agent development

### Key Benefits

- **Production Ready**: Built with enterprise-grade architecture and security
- **Scalable**: Designed to handle high-throughput agent evaluations
- **Extensible**: Plugin architecture for custom agents and evaluation metrics
- **Research-Grade**: Rigorous evaluation protocols and reproducible results
- **User-Friendly**: Modern web interface with real-time monitoring

---

## 🚀 Features

### 🤖 Agent Management

- **Multi-Provider Support**: OpenAI GPT-4/3.5, Anthropic Claude, Azure OpenAI, Ollama, HuggingFace
- **Dynamic Configuration**: Runtime API key management with secure handling
- **Custom Agents**: Support for user-defined agents through standardized interface
- **Performance Tracking**: Comprehensive metrics and historical analysis
- **Type Safety**: Full type hints and validation throughout

### 📊 Evaluation System

- **WebArena-Inspired Tasks**: Complex, multi-step realistic web scenarios
- **Isolated Environments**: Docker-based environment provisioning for reproducibility
- **Comprehensive Metrics**: Task completion rate, efficiency, execution time, success criteria
- **Real-time Monitoring**: Live execution tracking with detailed logging
- **Robust Scoring**: Standardized evaluation protocols with multiple scoring strategies

### 🏆 Analytics & Insights

- **Task-specific Rankings**: Detailed performance comparisons across different scenarios
- **Global Leaderboards**: Cross-task performance analysis and agent benchmarking
- **Advanced Analytics**: Performance trends, execution heatmaps, and detailed insights
- **User Dashboards**: Personalized performance tracking and progress monitoring
- **Export Capabilities**: Data export for research and analysis

### 🔧 Technical Excellence

- **Clean Architecture**: Repository pattern, dependency injection, and separation of concerns
- **Async Performance**: High-performance async/await architecture throughout
- **Comprehensive Testing**: Unit tests, integration tests, and end-to-end testing
- **Security**: JWT authentication, input validation, and secure API design
- **Monitoring**: Structured logging, error tracking, and performance monitoring

---

## 🏗️ Architecture

AgentArena follows a layered architecture with clean separation of concerns:

```mermaid
graph TB
    subgraph "Presentation Layer"
        UI[React Frontend]
        API[FastAPI REST API]
        WS[WebSocket Real-time]
    end

    subgraph "Application Layer"
        CTR[Controllers]
        MID[Middleware]
        VAL[Validators]
    end

    subgraph "Business Logic Layer"
        SVC[Services]
        FAC[Factories]
        STR[Strategies]
    end

    subgraph "Data Access Layer"
        REPO[Repositories]
        MOD[ORM Models]
        SCH[Schemas]
    end

    subgraph "Infrastructure Layer"
        DB[(Database)]
        EXT[External APIs]
        MON[Monitoring]
    end

    UI --> API
    API --> CTR
    CTR --> SVC
    SVC --> REPO
    REPO --> DB
```

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Git**

### One-Command Setup

```bash
git clone https://github.com/yourusername/agentarena.git
cd agentarena
chmod +x start_platform.sh
./start_platform.sh
```

The platform will be available at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 🔧 Installation

### Backend Setup

```bash
# Navigate to server directory
cd Server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python setup_database.py

# Create admin user
python setup_admin.py

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to client directory
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

### Docker Setup

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in the Server directory:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./agent_arena.db
# For PostgreSQL: DATABASE_URL=postgresql+asyncpg://user:password@localhost/agentarena

# Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:3000"]

# LLM Provider Settings (Optional - can be set per agent)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Playground Settings
USE_REAL_PLAYGROUND=false
MAX_EXECUTION_TIME=600
MAX_STEPS_PER_TASK=50

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agentarena.log
```

### Frontend Configuration

Create `.env.local` in the client directory:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
VITE_ENV=development
```

---

## 📖 Usage

### Creating an Agent

1. **Register/Login** to the platform
2. **Navigate** to Agent Management
3. **Click** "Create New Agent"
4. **Configure** your agent:
   ```json
   {
     "name": "My Custom Agent",
     "provider": "openai",
     "model": "gpt-4",
     "api_key": "your-key-here",
     "configuration": {
       "temperature": 0.7,
       "max_tokens": 2000
     }
   }
   ```

### Running Evaluations

1. **Select** a task from the Task Library
2. **Choose** your agent
3. **Configure** evaluation parameters
4. **Start** evaluation and monitor progress
5. **Review** results and metrics

### Viewing Results

- **Individual Results**: Detailed execution logs and metrics
- **Comparative Analysis**: Compare multiple agents across tasks
- **Leaderboards**: Global and task-specific rankings
- **Analytics**: Performance trends and insights

---

## 📚 API Documentation

### Authentication

```bash
# Register
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "securepassword",
  "role": "USER"
}

# Login
POST /api/v1/auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=securepassword
```

### Agent Management

```bash
# Create Agent
POST /api/v1/agents
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Agent",
  "agentType": "gpt-4",
  "llmApiKey": "encrypted-key",
  "configuration": {}
}

# List Agents
GET /api/v1/agents
Authorization: Bearer <token>

# Get Agent Details
GET /api/v1/agents/{agent_id}
Authorization: Bearer <token>
```

### Task Execution

```bash
# Submit Task
POST /api/v1/submissions
Authorization: Bearer <token>
Content-Type: application/json

{
  "agentId": "agent-uuid",
  "taskId": "task-uuid",
  "runConfig": {}
}

# Get Submission Status
GET /api/v1/submissions/{submission_id}
Authorization: Bearer <token>
```

For complete API documentation, visit http://localhost:8000/docs when running the server.

---

## 🛠️ Development

### Project Structure

```
AgentArena/
├── Server/                 # Backend (FastAPI)
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── controllers/   # Request handlers
│   │   ├── services/      # Business logic
│   │   ├── repositories/  # Data access
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── core/          # Core utilities
│   ├── tests/             # Backend tests
│   └── requirements.txt
├── client/                # Frontend (React)
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── store/         # State management
│   │   └── utils/         # Utilities
│   └── package.json
├── docs/                  # Documentation
├── docker-compose.yml     # Docker configuration
└── README.md
```

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes following the coding standards
4. **Test** your changes: `pytest` (backend), `npm test` (frontend)
5. **Commit** with conventional commits: `git commit -m "feat: add amazing feature"`
6. **Push** to your branch: `git push origin feature/amazing-feature`
7. **Submit** a pull request

### Testing

```bash
# Backend tests
cd Server
pytest tests/ -v --cov=app

# Frontend tests
cd client
npm test

# End-to-end tests
npm run test:e2e
```

### Code Quality

```bash
# Backend linting
cd Server
flake8 app/
black app/
mypy app/

# Frontend linting
cd client
npm run lint
npm run format
```

---

## 🚀 Deployment

### Production Deployment

1. **Environment Setup**:

   ```bash
   # Set production environment variables
   export DATABASE_URL=postgresql://...
   export SECRET_KEY=production-secret
   export ALLOWED_ORIGINS='["https://yourdomain.com"]'
   ```

2. **Database Migration**:

   ```bash
   cd Server
   alembic upgrade head
   ```

3. **Build Frontend**:

   ```bash
   cd client
   npm run build
   ```

4. **Deploy with Docker**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Security Considerations

- Use environment variables for sensitive configuration
- Enable HTTPS in production
- Implement rate limiting
- Regular security updates
- Database encryption at rest
- Secure API key handling

---
