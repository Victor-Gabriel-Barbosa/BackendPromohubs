import re
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import requests
from config import API_URL, KABUM_URL
import time

def rodar_periodicamente(intervalo_minutos=30):
  while True:
    try:
      extrair_e_enviar_ofertas()
    except Exception as e:
      print(f"Erro inesperado durante o scraping: {e}")

    print(f"Aguardando {intervalo_minutos} minutos até a próxima busca...\n")
    time.sleep(intervalo_minutos * 60)

def limpar_preco(preco_texto):
  """Extrai o valor numérico de textos como 'R$1.234,56' e converte para float."""
  if not preco_texto or preco_texto == "N/A":
    return None

  match = re.search(r'([\d.]+,\d{2})', preco_texto)
  if not match:
    return None

  valor_limpo = match[1].replace('.', '').replace(',', '.')
  try:
    return float(valor_limpo)
  except ValueError:
    return None


def _pegar_html(url: str) -> str:
  with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.goto(url)
    html = page.content()
    context.close()
    browser.close()
  return html


def extrair_e_enviar_ofertas():
  print("Buscando ofertas no Kabum...\n")

  # limpa as ofertas antigas antes de inserir as novas
  try:
    requests.delete(f"{API_URL}/kabum")
  except requests.exceptions.ConnectionError:
    print("Não foi possível limpar ofertas antigas (API fora do ar).")
    return
  
  html = _pegar_html(KABUM_URL)
  soup = BeautifulSoup(html, 'html.parser')

  itens = soup.find_all('a', class_=re.compile(r'flex flex-col relative gap-4 p-8'))

  if not itens:
    print("Nenhuma oferta encontrada. O HTML do Kabum pode ter mudado.")
    return

  # Cria uma sessão para reaproveitar conexões TCP nas chamadas à API
  with requests.Session() as session:
    for item in itens:
      nome_tag = item.select_one('span.line-clamp-2')
      desconto_tag = item.select_one('span.text-green-700')
      link = item.get('href', '')
      spans_preco = item.select('span.text-base.font-semibold.text-gray-800')

      img_tag = item.find('img')
      if img_tag:
        imagem_url = (
          img_tag.get('src')
          or img_tag.get('data-src')
          or (img_tag.get('data-srcset', '') or '').split(' ')[0]
          or (img_tag.get('srcset', '') or '').split(' ')[0]
        )
      else:
        imagem_url = None

      preco_texto = (
        "".join(span.get_text(strip=True) for span in spans_preco)
        if spans_preco else None
      )

      nome = nome_tag.get_text(strip=True) if nome_tag else "N/A"

      dados_oferta = {
        "nome": nome,
        "preco": limpar_preco(preco_texto),
        "desconto": desconto_tag.get_text(strip=True) if desconto_tag else None,
        "link": f"https://www.kabum.com.br{link}",
        "imagem": imagem_url or None,
      }

      try:
        resposta_api = session.post(f"{API_URL}/kabum", json=dados_oferta)
        if resposta_api.ok:
          print(f"[OK] Salvo com sucesso: {nome}")
        else:
          print(f"[ERRO] Erro ao salvar {nome} (Status {resposta_api.status_code}): {resposta_api.text}")
      except requests.exceptions.ConnectionError:
        print("Erro de conexão com a API. Verifique se o servidor FastAPI está rodando.")
        break


if __name__ == '__main__':
  rodar_periodicamente(intervalo_minutos=30)