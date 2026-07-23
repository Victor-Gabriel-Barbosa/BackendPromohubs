import re
import requests
from playwright.sync_api import Playwright, sync_playwright
from bs4 import BeautifulSoup

def run(playwright: Playwright) -> None:
  browser = playwright.chromium.launch(headless=True)
  context = browser.new_context()
  page = context.new_page()
  page.goto("https://www.kabum.com.br/ofertas/ofertasdodia")
  
  html = page.content()
  context.close()
  browser.close()

  return html

with sync_playwright() as playwright:
  resultado_final = run(playwright)
  soup = BeautifulSoup(resultado_final, 'html.parser')

  itens = soup.find_all('a', class_=re.compile(r'flex flex-col relative gap-4 p-8'))
  print(f"numero de itens igual a {len(itens)}")

for item in itens:
  nome = item.select_one('span.line-clamp-2')
  desconto = item.select_one('span.text-green-700')
  link = item.get('href', '')
  spans_preco = item.select('span.text-base.font-semibold.text-gray-800')

  img_tag = item.find('img')
  if img_tag:
    imagem_url = (
      img_tag.get('src')
      or img_tag.get('data-src')
      or img_tag.get('data-srcset', '').split(' ')[0]
      or img_tag.get('srcset', '').split(' ')[0]
    )
  else:
    imagem_url = 'N/A'

  if spans_preco:
    preco_formatado = "".join([span.get_text(strip=True) for span in spans_preco])
  else:
    preco_formatado = 'N/A'

  nome_str = nome.get_text(strip=True) if nome else 'N/A'
  desconto_str = desconto.get_text(strip=True) if desconto else 'N/A'
  link_completo = f"https://www.kabum.com.br{link}" if link else None

  oferta = {
    "nome": nome_str,
    "preco": preco_formatado,
    "desconto": desconto_str,
    "link": link_completo,
    "imagem": imagem_url,
    "publicado": True
  }

  url_api = "http://localhost:8000/ofertas-kabum"
  try:
    response = requests.post(url_api, json=oferta)
    if response.status_code == 201:
      print(f"Oferta salva com sucesso: {nome_str}")
    else:
      print(f"Falha ao salvar a oferta. Status Code: {response.status_code} - Erro: {response.text}")
  except requests.exceptions.RequestException as e:
    print(f"Erro de conexão com a API: {e}")