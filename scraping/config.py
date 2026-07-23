from dotenv import load_dotenv
import os

# Informações de acesso
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
API_URL = os.getenv("API_URL")
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
STEAM_URL = os.getenv("STEAM_URL")

# Grupos a monitorar
GRUPOS = [
  '@SamuelF3lipePromo',
  '@BenchPromos',
  "@PoisonPromos"
]

# Tipo de imagem padrão para conversão Base64
MIME = "image/jpeg"