import sys
import os

# Add backend directory to Python path so that the app modules can be resolved correctly
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app
