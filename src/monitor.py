import base64
from telethon.sync import TelegramClient
from telethon import events
import aiohttp
from utils import extrair_promocao
from config import API_ID, API_HASH, API_URL, GRUPOS, MIME

# Inicializa o cliente do Telegram
client = TelegramClient('sessao_scraper', API_ID, API_HASH)

# Evento para novas mensagens
@client.on(events.NewMessage(chats=GRUPOS))
async def nova_mensagem(event):
  mensagem = event.message
  print(f'\nNova mensagem em: {event.chat.title}')

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
    return
  
  # Extrai o tipo (produto ou cupom) e os dados da promoção
  tipo, dados = promo

  # Envia os dados para a API
  async with aiohttp.ClientSession() as session:
    try:
      async with session.post(f"{API_URL}/{tipo}", json=dados) as response:
        if response.status == 201:
          print(f"Sucesso: {tipo[:-1].capitalize()} salvo na API.")
        else:
          erro = await response.text()
          print(f"Erro ao salvar na API: {response.status} - {erro}")
    except aiohttp.ClientError as e:
      print(f"Erro de conexão com a API: {e}")

async def main():
  print('Monitorando novas mensagens...')
  print('Pressione CTRL+C para parar.\n')
  await client.run_until_disconnected()

# Inicializa o cliente em loop assíncrono
with client:
  client.loop.run_until_complete(main())