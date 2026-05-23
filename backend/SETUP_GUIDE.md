# Cash Management System - Setup Guide for Python 3.14

## 📋 Prerequisites

- **Python 3.14.0** (confirmed installed on your system)
- **pip** (package manager - comes with Python)
- **Git** (optional, for version control)
- **8GB RAM** (recommended for development)
- **Windows/Mac/Linux** (all supported)

## 🚀 Quick Start (5 minutes)

### Step 1: Open Terminal/PowerShell

Navigate to the backend directory:
```powershell
cd "C:\Users\padala.navika\OneDrive - Mphasis\Desktop\Cash Flow - Vibe Coding\backend"
```

### Step 2: Verify Python 3.14 Installation

```powershell
python --version
```

Expected output: `Python 3.14.0` (or similar 3.14.x)

### Step 3: Create Virtual Environment

```powershell
python -m venv venv
```

This creates an isolated Python environment for the project.

### Step 4: Activate Virtual Environment

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
.\venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate
```

You should see `(venv)` prefix in your terminal prompt when activated.

### Step 5: Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### Step 6: Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs all required packages for Python 3.14:
- **FastAPI 0.115.0** - Web framework
- **SQLAlchemy 2.1.5** - ORM
- **Pydantic 2.10.4** - Data validation
- **PyJWT 2.10.1** - JWT tokens
- **bcrypt 4.2.0** - Password hashing
- And 10+ other dependencies (all Python 3.14 compatible)

### Step 7: Initialize Database

```powershell
python -c "from app.database.db import init_db; init_db()"
```

This creates the SQLite database and all tables.

### Step 8: Start the Server

```powershell
uvicorn app.main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Step 9: Test the API

Open browser and visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

You should see interactive API documentation.

---

## 🔧 Troubleshooting

### Error: `Python 3.14 not found`

Make sure Python 3.14 is installed:
```powershell
py --list-paths
```

Look for `Python 3.14`. If not found, download from https://www.python.org/downloads/

### Error: `ModuleNotFoundError: No module named 'fastapi'`

Make sure virtual environment is activated (you should see `(venv)` in terminal):
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Error: `pip install -r requirements.txt` fails

Try upgrading setuptools and wheel first:
```powershell
python -m pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

Or install packages individually:
```powershell
pip install fastapi==0.115.0
pip install sqlalchemy==2.1.5
pip install pydantic==2.10.4
# etc...
```

### Error: Database initialization fails

Make sure you're in the correct directory and have activated venv:
```powershell
pwd  # Check current directory
.\venv\Scripts\Activate.ps1  # Reactivate if needed
python -c "from app.database.db import init_db; init_db()"
```

### Error: Port 8000 already in use

Use a different port:
```powershell
uvicorn app.main:app --reload --port 8001
```

### Error: Virtual environment won't activate

Try using absolute paths:
```powershell
cd C:\Users\padala.navika\OneDrive\ -\ Mphasis\Desktop\Cash\ Flow\ -\ Vibe\ Coding\backend
C:\Users\padala.navika\OneDrive\ -\ Mphasis\Desktop\Cash\ Flow\ -\ Vibe\ Coding\backend\venv\Scripts\Activate.ps1
```

---

## 📦 Dependencies Explanation

| Package | Version | Purpose |
|---------|---------|---------|
| FastAPI | 0.115.0 | REST API web framework |
| SQLAlchemy | 2.1.5 | Database ORM |
| Pydantic | 2.10.4 | Data validation & serialization |
| PyJWT | 2.10.1 | JWT token handling |
| bcrypt | 4.2.0 | Password hashing |
| cryptography | 44.0.0 | Encryption utilities |
| python-dotenv | 1.0.1 | Environment variables |
| uvicorn | 0.32.0 | ASGI server |
| pytest | 8.3.4 | Testing framework |
| pytest-asyncio | 0.24.0 | Async test support |
| httpx | 0.28.1 | HTTP client for testing |

All packages are compatible with **Python 3.14.0**.

---

## 📁 Project Structure After Setup

```
backend/
├── venv/                          # Virtual environment (created)
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/         # 6 endpoint files
│   ├── database/
│   │   ├── models.py             # 11 ORM models
│   │   └── db.py                 # Database initialization
│   ├── services/                 # 6 service files
│   ├── repositories/             # 8 repository files
│   ├── auth/                     # JWT & password handling
│   ├── exceptions/               # Custom exceptions
│   ├── models/                   # Pydantic schemas
│   ├── utils/                    # Business logic & helpers
│   ├── validators/               # Input validation
│   ├── config.py                 # Configuration
│   └── main.py                   # FastAPI app factory
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .env                          # Environment (created)
└── install.py                    # Installation script
```

---

## 🧪 Verify Installation

After setup, run these commands to verify everything works:

```powershell
# Check Python version
python --version

# Check FastAPI
python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"

# Check SQLAlchemy
python -c "import sqlalchemy; print(f'SQLAlchemy {sqlalchemy.__version__}')"

# Check Pydantic
python -c "import pydantic; print(f'Pydantic {pydantic.__version__}')"

# Check app loads
python -c "from app.main import app; print('✓ FastAPI app initialized')"

# Check database
python -c "from app.database.db import init_db; init_db(); print('✓ Database initialized')"
```

All commands should show version numbers without errors.

---

## 🎯 Quick Test API Calls

Once server is running at http://localhost:8000:

### 1. Register User
```powershell
$headers = @{"Content-Type" = "application/json"}
$body = @{
    username = "testuser"
    email = "test@example.com"
    password = "Password123!"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/register" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

### 2. Login
```powershell
$body = @{
    username = "testuser"
    password = "Password123!"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -Headers $headers `
    -Body $body
```

### 3. Use Swagger UI (Easier!)
Just visit: http://localhost:8000/api/docs

Click "Try it out" on any endpoint to test.

---

## 🔒 Environment Configuration

The `.env` file contains important settings:

```env
# Database
DATABASE_URL=sqlite:///./cash_management.db

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=Cash Management System
DEBUG=True
```

⚠️ **In production, change SECRET_KEY to a secure random string!**

---

## 📝 Common Commands

```powershell
# Activate environment
.\venv\Scripts\Activate.ps1

# Run server
uvicorn app.main:app --reload

# Run tests
pytest

# Run specific test file
pytest tests/test_debit_service.py

# Run with coverage
pytest --cov=app --cov-report=html

# Format code
black app/

# Lint code
flake8 app/

# Type check
mypy app/

# Deactivate environment
deactivate
```

---

## 🚀 Production Deployment

Before deploying:

1. **Set DEBUG=False** in `.env`
2. **Generate new SECRET_KEY**
3. **Use production database** (PostgreSQL recommended)
4. **Configure HTTPS/SSL**
5. **Set up environment variables** on deployment platform
6. **Use production ASGI server** (gunicorn, etc.)

See deployment documentation for detailed instructions.

---

## 📞 Support & Documentation

- **API Documentation**: http://localhost:8000/api/docs (when running)
- **ReDoc**: http://localhost:8000/api/redoc
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Pydantic Docs**: https://docs.pydantic.dev/

---

## ✅ Setup Checklist

- [ ] Python 3.14 installed
- [ ] Terminal opened in backend directory
- [ ] Virtual environment created
- [ ] Virtual environment activated
- [ ] pip upgraded
- [ ] Dependencies installed
- [ ] Database initialized
- [ ] Server started on http://localhost:8000
- [ ] Swagger UI accessible at http://localhost:8000/api/docs
- [ ] Environment file (.env) created

If all checkboxes are complete, your setup is ready! 🎉
