from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

PAYMENTS_TOKEN = '381764678:TEST:79061'


class Settings(BaseSettings):
    bot_token: SecretStr
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()
