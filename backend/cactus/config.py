import logging
from functools import lru_cache
from pathlib import Path
from uuid import UUID

from pydantic import DirectoryPath
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    host: str = '127.0.0.1'
    port: int = 9991
    workers: int = 1
    reload: bool = False
    logging_level: int = logging.INFO

    cloud_api_key: str = 'EXO...'
    cloud_api_secret: str = 'PJt...'
    cloud_zone: str = 'de-fra-1'
    cloud_template_id: UUID = UUID(int=0)
    cloud_security_group_id: UUID = UUID(int=0)
    cloud_host_url: str = 'https://example.com'

    jhub_port: int = 8080

    github_oauth_client_id: str = ''
    github_oauth_client_secret: str = ''

    path_hash: str = '/path-hash'
    frontend_folder_path: DirectoryPath = Field(default_factory=lambda: Path(__file__).parents[2] / 'frontend')


@lru_cache(1)
def get_settings() -> Settings:
    return Settings()
