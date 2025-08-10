# PathCraft: AI-Powered Goal Decomposition & Smart Scheduling Platform 🚀

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**PathCraft** is an intelligent productivity platform that leverages AI and machine learning to help users break down complex goals into manageable tasks, optimize scheduling, and maintain motivation through adaptive reminders. Built with a modern Python backend and featuring advanced ML algorithms for personalized productivity optimization.

## 🌟 Key Features

### 🎯 **Smart Goal Management**
- **AI-Powered Decomposition**: Automatically break down large goals into actionable sub-goals and tasks
- **Hierarchical Organization**: Multi-level goal structure with parent-child relationships
- **Progress Tracking**: Visual progress indicators and milestone management

### ⏰ **Intelligent Scheduling**
- **ML-Based Optimization**: Machine learning algorithms analyze user behavior patterns
- **Adaptive Scheduling**: Learn from productivity patterns to suggest optimal time slots
- **Conflict Resolution**: Smart conflict detection and resolution with existing calendar events
- **Priority-Based Allocation**: Automatically prioritize tasks based on deadlines and importance

### 🔔 **Smart Notifications & Reminders**
- **Behavioral Learning**: Adapts reminder timing based on user response patterns
- **Multi-Channel Delivery**: Email, push notifications, and calendar integration
- **Context-Aware**: Sends reminders when users are most likely to be productive

### 👥 **Team Collaboration**
- **OKR Management**: Set and track team objectives and key results
- **Role-Based Access**: Granular permissions for team members
- **Progress Sharing**: Real-time updates and collaborative goal tracking

### 📊 **Analytics & Insights**
- **Productivity Metrics**: Track completion rates, focus time, and efficiency
- **Pattern Recognition**: Identify optimal working hours and productivity windows
- **Performance Reports**: Detailed analytics for continuous improvement

## 🏗️ Architecture Overview

```
PathCraft/
├── backend/                 # FastAPI Backend Server
│   ├── api/                # REST API Endpoints
│   ├── core/               # Core Business Logic
│   ├── ml/                 # Machine Learning Models
│   ├── models/             # Database Models & Schemas
│   └── database.py         # Database Configuration
├── frontend/               # Frontend Components (Flutter/Dart)
├── ml/                     # ML Training & Models
├── prototype/              # HTML/CSS/JS Prototype
├── tests/                  # Test Suite
└── database/               # Database Migrations
```

### **Backend Architecture**
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and serialization
- **WebSocket**: Real-time communication for live updates

### **Machine Learning Components**
- **Enhanced Scheduler**: Random Forest-based scheduling optimization
- **Reminder Optimizer**: Behavioral pattern learning for optimal notification timing
- **Slot Optimizer**: Time slot recommendation engine
- **User Behavior Analysis**: Pattern recognition for productivity optimization

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Virtual Environment** (recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/pathcraft.git
cd pathcraft
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio httpx
```

### 4. Database Setup

```bash
# The application will automatically create SQLite database
# For production, you can configure PostgreSQL in database.py
```

### 5. Run the Backend Server

```bash
# Start the FastAPI server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Your API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 6. Run the Prototype Frontend

```bash
# Open prototype/index.html in your browser
# Or serve it with a simple HTTP server:
python -m http.server 8080
# Then visit: http://localhost:8080/prototype/
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_backend.py

# Run tests with verbose output
pytest -v
```

## 📚 API Documentation

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users/` | POST | User registration |
| `/api/token` | POST | User authentication |
| `/api/goals/` | GET/POST | Goal management |
| `/api/sub_goals/` | GET/POST | Sub-goal management |
| `/api/tasks/` | GET/POST | Task management |
| `/api/teams/` | GET/POST | Team management |
| `/api/notifications/` | GET/POST | Notification system |

### Authentication

All protected endpoints require Bearer Token authentication:

```bash
curl -H "Authorization: Bearer <your_token>" \
     http://localhost:8000/api/goals/
```

### Example API Usage

```bash
# Create a new user
curl -X POST "http://localhost:8000/api/users/" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "securepassword"}'

# Login and get token
curl -X POST "http://localhost:8000/api/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=securepassword"

# Create a goal
curl -X POST "http://localhost:8000/api/goals/" \
     -H "Authorization: Bearer <your_token>" \
     -H "Content-Type: application/json" \
     -d '{"title": "Learn Machine Learning", "target_date": "2024-12-31", "methodology": "Online courses and projects"}'
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DATABASE_URL=sqlite:///./pathcraft.db
# For PostgreSQL: postgresql://user:password@localhost/pathcraft

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Model Paths
SCHEDULER_MODEL_PATH=enhanced_scheduler_model.pkl
REMINDER_MODEL_PATH=reminder_optimizer_model.pkl

# External Services
CALENDAR_API_KEY=your-calendar-api-key
SLACK_WEBHOOK_URL=your-slack-webhook-url
```

### Database Configuration

The application supports both SQLite (development) and PostgreSQL (production):

```python
# backend/database.py
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pathcraft.db")
```

## 🚀 Deployment

### Production Setup

1. **Install Production Dependencies**
   ```bash
   pip install gunicorn uvicorn[standard]
   ```

2. **Configure Environment Variables**
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/pathcraft"
   export SECRET_KEY="your-production-secret-key"
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## 📁 Project Structure Details

### Backend Components

- **`api/`**: REST API endpoints for all features
- **`core/`**: Core business logic and algorithms
- **`ml/`**: Machine learning models and training scripts
- **`models/`**: Database models and Pydantic schemas
- **`database.py`**: Database connection and session management

### Frontend Components

- **`frontend/lib/widgets/`**: Flutter/Dart UI components
- **`prototype/`**: HTML/CSS/JS prototype for rapid testing

### Machine Learning

- **`ml/enhanced_scheduler.py`**: AI-powered scheduling optimization
- **`ml/reminder_optimizer.py`**: Smart reminder timing
- **`ml/slot_optimizer.py`**: Time slot recommendation engine

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure SQLite file has write permissions
   - Check database path in `database.py`

2. **Import Errors**
   - Verify virtual environment is activated
   - Check Python path and dependencies

3. **Port Already in Use**
   - Change port: `uvicorn backend.main:app --port 8001`
   - Kill existing process: `lsof -ti:8000 | xargs kill -9`

### Getting Help

- Check the [API Reference](backend/API_REFERENCE.md)
- Review test files for usage examples
- Open an issue on GitHub with detailed error information

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI community for the excellent web framework
- SQLAlchemy for robust database operations
- Scikit-learn for machine learning capabilities
- All contributors who help improve PathCraft

---

**Ready to transform your productivity? Start with PathCraft today! 🚀**

For questions, support, or contributions, please open an issue or reach out to our team.