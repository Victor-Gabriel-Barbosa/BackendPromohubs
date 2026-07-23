import re
from itertools import islice

# Formatação e limpeza de texto
RE_FORMATACAO_MD = re.compile(r'[*_~`]')
RE_QUEBRA_LINHA = re.compile(r'\n+')

# Limpeza do nome do produto
RE_HASHTAG = re.compile(r'#[^\s]+')
RE_SEPARADOR_PRECO = re.compile(r'\s*-\s*R\$|\s+R\$')
RE_CARACTERES_ESPECIAIS = re.compile(r'[^\w\s,.\-!?\'/()+:%]')
RE_ESPACOS_MULTIPLOS = re.compile(r'\s+')

# Extração de dados (preços, cupons e links)
RE_PRECO = re.compile(r'R\$\s*([\d.,]+)')
RE_PORCENTAGEM = re.compile(r'(\d+)%\s*(?i:off)?')
RE_CUPOM = re.compile(r'(?i)(?:cupom|cupons):\s*([^\n]+)')
RE_CUPOM_ALTERNATIVO = re.compile(r': \s*([^\n]+)')
RE_URL = re.compile(r'https?://\S+')

# Linhas a ignorar na busca pelo nome (alertas + links) e detecção de cupom
RE_LINHA_IGNORAR = re.compile(r'parcelado!|baixou!|preço histórico!|vídeo novo|http', re.IGNORECASE)
RE_EH_CUPOM = re.compile(r'cupom|cupons', re.IGNORECASE)

# Limpa os valores extraídos no padrão decimal
def _limpar_valor(valor: str | None) -> str | None:
  if not valor:
    return None

  # Remove pontos (milhar) e substitui vírgula por ponto (decimal)
  valor_limpo = valor.strip().replace('.', '').replace(',', '.')

  # Remove o ponto final caso a string termine com ele (ex: "1199.")
  if valor_limpo.endswith('.'):
    valor_limpo = valor_limpo[:-1]

  return valor_limpo

# Normaliza o texto, removendo formatações comuns do Telegram e links
def _normalizar_texto(texto: str) -> str:
  texto = RE_FORMATACAO_MD.sub('', texto)
  texto = RE_QUEBRA_LINHA.sub('\n', texto)
  return texto

# Normaliza o nome do produto, removendo hashtags, preços e caracteres indesejados
def _normalizar_nome(nome: str) -> str:
  nome = RE_HASHTAG.sub('', nome)
  if match := RE_SEPARADOR_PRECO.search(nome):
    nome = nome[:match.start()]
  nome = RE_CARACTERES_ESPECIAIS.sub('', nome)
  nome = RE_ESPACOS_MULTIPLOS.sub(' ', nome)
  return nome.strip(' -')

# Extrai o nome do produto, ignorando alertas comuns e links
def _extrair_nome(texto: str) -> str | None:
  for linha in texto.splitlines():
    linha = linha.strip()
    if linha and not RE_LINHA_IGNORAR.search(linha):
      return linha
  return None

# Encontra até `limite` preços no texto, sem escanear além do necessário
def _encontrar_precos(texto: str, limite: int) -> list[str]:
  return [m.group(1) for m in islice(RE_PRECO.finditer(texto), limite)]

# Extrai os dados de um cupom, considerando o valor do desconto e o limite mínimo
def _extrair_dados_cupom(texto: str) -> tuple[str | None, str | None]:
  precos = _encontrar_precos(texto, 2)
  desconto = _limpar_valor(precos[0]) if precos else None
  limite_minimo = _limpar_valor(precos[1]) if len(precos) > 1 else None

  if not desconto:
    desconto = f"{match[1]}%" if (match := RE_PORCENTAGEM.search(texto)) else None

  return desconto, limite_minimo

# Extrai os dados de um produto, considerando o preço à vista e o preço parcelado
def _extrair_dados_produto(texto: str) -> tuple[str | None, str | None]:
  precos = _encontrar_precos(texto, 3)

  match len(precos):
    case 0:
      return None, None
    case 1:
      return _limpar_valor(precos[0]), None
    case 2:
      return _limpar_valor(precos[0]), _limpar_valor(precos[1])
    case _:
      return _limpar_valor(precos[1]), _limpar_valor(precos[2])

# Extrai as informações relevantes de uma mensagem
def extrair_promocao(texto: str, imagem: str | None) -> tuple[str, dict] | None:
  if not texto:
    return None

  texto = _normalizar_texto(texto)

  if not (nome_bruto := _extrair_nome(texto)):
    return None

  nome = _normalizar_nome(nome_bruto)
  eh_cupom = bool(RE_EH_CUPOM.search(nome_bruto))
  desconto, limite_minimo = _extrair_dados_cupom(texto) if eh_cupom else (None, None)
  preco, preco_parcelado = (None, None) if eh_cupom else _extrair_dados_produto(texto)
  cupom = (match[1] if (match := RE_CUPOM.search(texto)) else None) or (match[1] if (match := RE_CUPOM_ALTERNATIVO.search(texto)) else None)
  link = match[0] if (match := RE_URL.search(texto)) else None

  if not (preco or preco_parcelado or desconto):
    print(f"Mensagem ignorada:{texto[:50]}")
    return None

  if (eh_cupom):
    return "cupons", {
      'nome': nome,
      'codigo': cupom,
      'desconto': desconto,
      'limite_minimo': limite_minimo,
      'link': link,
      'imagem': imagem
    }

  return "produtos", {
    'nome': nome,
    'preco': preco,
    'preco_parcelado': preco_parcelado,
    'link': link,
    'cupom': cupom,
    'imagem': imagem
  }