from pydantic import BaseSettings

class Settings(BaseSettings):
    project_name: str = "zapier-clone"
    debug: bool = True

settings = Settings()
