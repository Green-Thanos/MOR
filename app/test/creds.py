import os
from dotenv import load_dotenv
import os

load_dotenv()

env = os.getenv('GOOGLE_CREDENTIALS_JSON')

config_path = os.getenv('COLUMN_CONFIG', 'columnValues.json')


print(env)