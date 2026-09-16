from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "TripForge")
APP_ENV = os.getenv("APP_ENV", "development")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/")
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173/")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tripforge.db")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ASSOCIATION_EMAIL = os.getenv("ASSOCIATION_EMAIL", "admin@gmail.com")
ASSOCIATION_PASSWORD = os.getenv("ASSOCIATION_PASSWORD", "admin123")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", "TripForge <onboarding@resend.dev>")
