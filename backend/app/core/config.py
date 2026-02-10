from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
	project_name: str = "zapier-clone"
	debug: bool = True

	# Important secrets / connection strings
	database_url: Optional[str] = None
	secret_key: Optional[str] = None
	redis_url: Optional[str] = None
	celery_broker_url: Optional[str] = None

	class Config:
		# load environment variables from backend/.env when running from repo root
		env_file = ".env"
		env_file_encoding = "utf-8"


settings = Settings()
