from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str('TOKEN_ID')
ADMIN_ID = env.str('ADMIN_ID')

