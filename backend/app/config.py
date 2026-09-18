from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str = "dev-secret-key-change-me"

    admin_username: str = "admin"
    admin_password: str = "admin"
    checkin_username: str = "checkin"
    checkin_password: str = "checkin"

    database_url: str = "sqlite:///./data/confra.db"
    upload_dir: str = "./uploads"
    public_base_url: str = "http://localhost:37230"

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_use_tls: bool = True
    email_from: str = "confraternizacao@sead.go.gov.br"

    evento_valor_inscricao: str = "0,00"

    access_token_expire_minutes: int = 480

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
