import os
import environ as environ
import dotenv

dotenv.load_dotenv(os.environ.get("ENV_PATH", None))

@environ.config()
class Jwt:
    secret: str = environ.var()

@environ.config()
class Password:
    salt: str = environ.var()
    token_key: str = environ.var()


@environ.config(prefix="")
class Config:
    """
    class config
    """
    db: str = environ.var()
    jwt: Jwt = environ.group(Jwt)
    password: Password = environ.group(Password)


cfg: Config = environ.to_config(Config)