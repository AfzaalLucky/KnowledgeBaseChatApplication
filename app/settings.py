from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    qdrant_url: str = "http://localhost:6333"
    collection_name: str = "kb_chat"

    embedding_model: str = "nomic-embed-text"
    chat_model: str = "llama3.2"
    embedding_dim: int = 768

    sql_connection: str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=KnowledgeBase;"
        "Trusted_Connection=yes;"
    )

    allowed_origins: list[str] = ["http://localhost:5173"]

    upload_dir: str = "data/documents"
    max_upload_mb: int = 25
    allowed_extensions: list[str] = [".pdf", ".docx", ".txt"]

    max_question_length: int = 2000


settings = Settings()
