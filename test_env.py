# test_env.py
from src.core.config import settings
print("DATABASE_URI desde config:", settings.SQLALCHEMY_DATABASE_URI)