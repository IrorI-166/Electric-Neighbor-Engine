import os
from os.path import join, dirname
from dotenv import load_dotenv

load_dotenv(verbose=True)

env_path = "MOD_Create_Data/API-keys.env"
load_dotenv(env_path)

BT = os.environ.get("Bearer_Token")