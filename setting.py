from pydantic import BaseSettings, dataclasses

class Config(BaseSettings):
    login_url = 'https://passport.jd.com/new/login.aspx'

@dataclasses.dataclass
class InfoUser:
    username: str
    password: str