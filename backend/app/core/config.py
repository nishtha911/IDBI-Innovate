from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    PROJECT_NAME: str = "IDBI Innovate Financial Health Card API"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"
    
    # Server configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Service settings
    ENABLE_MOCK_DELAY: bool = Field(
        default=True, 
        description="Simulate network delay for mock services to make it feel real"
    )
    MOCK_DELAY_SECONDS: float = 0.5
    
    USE_ML_MODEL: bool = Field(
        default=False, 
        description="Use the trained ML model for credit scoring instead of the rules-based engine"
    )
    
    GROQ_API_KEY: str | None = Field(
        default=None,
        description="Groq API key for LLM integration"
    )
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
