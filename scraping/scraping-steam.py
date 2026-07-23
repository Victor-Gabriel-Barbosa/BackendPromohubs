import requests
from playwright.sync_api import sync_playwright
from config import API_URL, STEAM_URL

def limpar_preco(preco_texto):
  """Remove o 'R$', espaços, trata jogos gratuitos e converte para float."""
  if not preco_texto or preco_texto == "N/A":
    return None
  
  # Tratamento para jogos gratuitos
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
  cookies_steam = [
    {'name': 'birthtime', 'value': '283993201', 'url': STEAM_URL},
    {'name': 'lastagecheckage', 'value': '1-January-1980', 'url': STEAM_URL},
    {'name': 'wants_mature_content', 'value': '1', 'url': STEAM_URL}
  ]

  print("Iniciando o navegador Playwright...\n")
  with sync_playwright() as p:
    # Inicia o navegador sem interface gráfica
    browser = p.chromium.launch(headless=True)
    
    # Cria um contexto aplicando os cabeçalhos (User-Agent e Localização)
    context = browser.new_context(
      user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      locale='pt-BR'
    )
    
    # Adiciona os cookies para burlar o aviso de idade
    context.add_cookies(cookies_steam)
    
    page = context.new_page()

    try:
      print("Buscando promoções na Steam...\n")
      # Navega até a página e aguarda o conteúdo principal carregar
      page.goto(STEAM_URL, wait_until='domcontentloaded')
      
      # Aguarda até que os resultados da pesquisa apareçam (timeout de 10s)
      try:
        page.wait_for_selector('a.search_result_row', timeout=10000)
      except Exception:
        print("Nenhum jogo encontrado. A Steam pode estar bloqueando silenciosamente ou o HTML mudou.")
        return

      # Coleta todas as tags de jogos
      jogos = page.locator('a.search_result_row').all()

      # Cria uma sessão do requests apenas para o envio dos dados para a API
      with requests.Session() as session:
        for jogo in jogos[:30]:
          url_jogo = jogo.get_attribute('href')

          # Extrai o título do jogo
          titulos = jogo.locator('span.title').all_text_contents()
          titulo = titulos[0].strip() if titulos else "Título não encontrado"
          
          # Extrai a URL da imagem do jogo
          imagem_locator = jogo.locator('img')
          imagem_url = imagem_locator.first.get_attribute('src') if imagem_locator.count() > 0 else None
          
          # Extrai o desconto (%)
          descontos = jogo.locator('div.discount_pct').all_text_contents()
          desconto = descontos[0].strip() if descontos else None
          
          # Extrai o preço original
          precos_originais = jogo.locator('div.discount_original_price').all_text_contents()
          preco_original = precos_originais[0].strip() if precos_originais else None
          
          # Extrai o preço final
          precos_finais = jogo.locator('div.discount_final_price').all_text_contents()
          preco_final = precos_finais[0].strip() if precos_finais else None
          
          dados_promocao = {
            "nome": titulo,
            "desconto": desconto,
            "preco_original": limpar_preco(preco_original),
            "preco_final": limpar_preco(preco_final),
            "link": url_jogo,
            "imagem": imagem_url
          }
          
          try:
            resposta_api = session.post(f"{API_URL}/promocoes", json=dados_promocao)
            
            if resposta_api.ok:
              print(f"[OK] Salvo com sucesso: {titulo}")
            else:
              print(f"[ERRO] Erro ao salvar {titulo} (Status {resposta_api.status_code}): {resposta_api.text}")
                  
          except requests.exceptions.ConnectionError:
            print("Erro de conexão com a API. Verifique se o servidor está rodando.")
            break

    except Exception as e:
      print(f"Erro ao acessar a página da Steam: {e}")
    finally:
      browser.close()

if __name__ == '__main__':
  extrair_e_enviar_promocoes()