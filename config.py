
from pydantic_settings import BaseSettings
import os
from typing import cast

class Config(BaseSettings):

    ENV: str = cast(str, os.getenv("ENV", "development"))
    PROJECT_DOMAIN_SUFFIX: str = cast(str, os.getenv("PROJECT_DOMAIN_SUFFIX"))
