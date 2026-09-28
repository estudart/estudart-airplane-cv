from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    WS_SERVER_URL: str = "ws://localhost:8080"
    SHOULD_PREDICT: bool = True
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    CAMERA_FRAME_KEY: str = "camera:latest"
    CAMERA_SOURCE: str = "0"
    CAMERA_WIDTH: int = 1280
    CAMERA_HEIGHT: int = 720
    CAMERA_FPS: int = 15
    MODEL_NAME: str = "yolo26n.pt"


settings = Settings()

