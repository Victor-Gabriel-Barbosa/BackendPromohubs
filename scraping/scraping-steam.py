import requests
from bs4 import BeautifulSoup
from config import API_URL, STEAM_URL

def limpar_preco(preco_texto):
  """Remove o 'R$', espaços, trata jogos gratuitos e converte para float."""
  if not preco_texto or preco_texto == "N/A":
    return None
  
  # Tratamento para jogos que ficaram 100% gratuitos
  texto_lower = preco_texto.lower()
  if "free" in texto_lower or "gratuito" in texto_lower:
    return 0.0
  
  # Remove 'R$', espaços não separáveis (\xa0) e espaços normais
  preco_limpo = preco_texto.replace('R$', '').replace('\xa0', '').replace(' ', '')
  preco_limpo = preco_limpo.replace(',', '.')
  
  try:
    return float(preco_limpo)
  except ValueError:
    return None

def extrair_e_enviar_promocoes():
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
  }
  
  cookies = {
    'birthtime': '283993201',
    'lastagecheckage': '1-January-1980',
    'wants_mature_content': '1'
  }

  # Cria uma sessão para reaproveitar conexões TCP
  with requests.Session() as session:
    try:
      print("Buscando promoções na Steam...\n")
      resposta = session.get(STEAM_URL, headers=headers, cookies=cookies)
      resposta.raise_for_status() 
      
      soup = BeautifulSoup(resposta.text, 'html.parser')
      jogos = soup.find_all('a', class_='search_result_row')
      
      if not jogos:
        print("Nenhum jogo encontrado. A Steam pode estar bloqueando silenciosamente ou o HTML mudou.")
        return

      for jogo in jogos[:15]:
        url_jogo = jogo.get('href')

        titulo_tag = jogo.find('span', class_='title')
        titulo = titulo_tag.text.strip() if titulo_tag else "Título não encontrado"
        
        imagem_tag = jogo.find('img')
        imagem_url = imagem_tag.get('src') if imagem_tag else None
        
        desconto_tag = jogo.find('div', class_='discount_pct')
        desconto = desconto_tag.text.strip() if desconto_tag else None
        
        preco_original_tag = jogo.find('div', class_='discount_original_price')
        preco_original = preco_original_tag.text.strip() if preco_original_tag else None
        
        preco_final_tag = jogo.find('div', class_='discount_final_price')
        preco_final = preco_final_tag.text.strip() if preco_final_tag else None
        
        dados_promocao = {
          "nome": titulo,
          "desconto": desconto,
          "preco_original": limpar_preco(preco_original),
          "preco_final": limpar_preco(preco_final),
          "link": url_jogo,
          "imagem": imagem_url
        }
        
        try:
          # Usa a mesma sessão para fazer o POST na API
          resposta_api = session.post(f"{API_URL}/promocoes", json=dados_promocao)
          
          # Aceita qualquer status de sucesso (200, 201, etc)
          if resposta_api.ok:
            print(f"[OK] Salvo com sucesso: {titulo}")
          else:
            print(f"[ERRO] Erro ao salvar {titulo} (Status {resposta_api.status_code}): {resposta_api.text}")
              
        except requests.exceptions.ConnectionError:
          print("Erro de conexão com a API. Verifique se o servidor FastAPI está rodando.")
          break
                
    except requests.exceptions.RequestException as e:
      print(f"Erro ao acessar a página da Steam: {e}")

if __name__ == '__main__':
  extrair_e_enviar_promocoes()