import yaml
from pydantic import BaseModel, BaseSettings


class DSNSettings(BaseModel):
    host: str
    port: int
    dbname: str
    password: str
    user: str


class PostgresSettings(BaseSettings):
    dsn: DSNSettings
    query_limit: int
    state_file_path: str
    tables: list
    default_date: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'


class Settings(BaseModel):
    pg_conf: PostgresSettings
    es_url: str
    backoff_start_time: float
    backoff_border_time: float
    backoff_factor: int

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


with open('config.yaml', "r") as f:
    data = yaml.safe_load(f)


settings = Settings(**data)
