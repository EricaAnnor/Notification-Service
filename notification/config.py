from pydantic_settings import BaseSettings,SettingsConfigDict


class Settings(BaseSettings):
    db_name:str
    db_password:str
    db_user:str
    db_port:int
    sendgridapikey:str
    rabbitmqdefaultuser:str
    rabbitmqdefaultpassword:str
    account_sid:str
    auth_token:str
    phone_number:str
    api_key:str

    model_config = SettingsConfigDict(env_file=".env")
    




