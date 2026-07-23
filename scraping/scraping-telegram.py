import base64
from telethon.sync import TelegramClient
import aiohttp
from scraping.utils import extrair_promocao
from config import API_ID, API_HASH, API_URL, GRUPOS, MIME

# Inicializa o cliente do Telegram
client = TelegramClient('sessao_scraper', API_ID, API_HASH)

async def main():
  print("Conectado! Iniciando a coleta de mensagens...\n")

  contador = 0

  # Abre a sessão HTTP para reutilizar nas requisições
  async with aiohttp.ClientSession() as session:
    # Itera sobre os grupos para coletar mensagens
    for grupo in GRUPOS:
      print(f"-> Coletando mensagens de: {grupo}")
      try:
        async for mensagem in client.iter_messages(grupo, limit=30):
          # Baixa a imagem diretamente para memória
          imagem_bytes = await client.download_media(mensagem, bytes)
          
          # Converte para Base64
          imagem_base64 = (
            f"data:{MIME};base64,{base64.b64encode(imagem_bytes).decode()}"
            if imagem_bytes
            else None
          )
          
          # Tenta extrair a promoção
          if not (promo := extrair_promocao(mensagem.text, imagem_base64)):
            continue
          
          # Extrai o tipo (produto ou cupom) e os dados da promoção
          tipo, dados = promo
            
          # Dispara para a API usando JSON novamente
          try:
            async with session.post(f"{API_URL}/{tipo}", json=dados) as response:
              if response.status == 201:
                print(f"[OK] {tipo[:-1].capitalize()} enviado!")
                contador += 1
              else:
                print(f"[ERRO] Falha ao enviar {tipo}: Status {response.status}")
                print(f"Detalhes: {await response.text()}")
          except aiohttp.ClientError as e:
            print(f"Erro de conexão com a API: {e}")
              
      except Exception as e:
        print(f"Erro ao acessar o grupo {grupo}: {e}")

  print(f"\nFinalizado! {contador} promoções enviadas para a API.")

# Inicializa o cliente em loop assíncrono
with client:
  client.loop.run_until_complete(main())