#-------------------------------------Base Setting Module-----------------------------------
# BaseSettings in Pydantic is used to manage application configuration by automatically reading values 
# from environment variables or .env files, making apps more secure and flexible.
from pydantic.v1 import BaseSettings
class Settings(BaseSettings):
    authjwt_secret_key:str='af744f13e9af078c87e4c2292018fa582a99c913d74122eaa2fdb1f36a0dd6cf'