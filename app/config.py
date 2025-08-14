from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    eth_model_path: str = "trained_models/model_eth.onnx"
    allowed_origins: list[str] = ["*"]

settings = Settings()
