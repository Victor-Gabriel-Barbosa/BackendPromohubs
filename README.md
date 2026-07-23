# PromoHubs — Backend

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

API REST e conjunto de *scrapers* responsáveis por coletar, tratar e disponibilizar promoções, cupons e ofertas vindas de diferentes fontes — grupos do Telegram, Kabum e Steam — para alimentar a plataforma **PromoHubs**.

## 📋 Sobre o projeto

O backend é dividido em duas partes que trabalham em conjunto:

- **API (FastAPI + PostgreSQL)**: expõe endpoints CRUD para produtos, cupons, promoções da Steam, ofertas do Kabum e notas fiscais, servindo como fonte única de dados para o(s) consumidor(es) do PromoHubs.
- **Scrapers (Telethon + Playwright + BeautifulSoup)**: coletam promoções de grupos de Telegram em tempo real (ou em lote), além de raspar periodicamente ofertas do site do Kabum e promoções da Steam, enviando os dados extraídos para a própria API.

## ✨ Funcionalidades

- CRUD completo de produtos, cupons, promoções da Steam e ofertas do Kabum.
- Registro e consulta de notas fiscais.
- Monitoramento em tempo real de mensagens em grupos do Telegram (`monitor.py`).
- Coleta do histórico recente de mensagens dos grupos monitorados (`scraping-telegram.py`).
- Raspagem periódica (a cada 30 min, por padrão) das ofertas do Kabum, com limpeza automática das ofertas antigas antes de cada nova coleta.
- Raspagem das promoções em destaque da Steam.
- Extração automática de nome, preço, preço parcelado, desconto, cupom e link a partir do texto bruto das mensagens, via expressões regulares (`utils.py`).

## 🏗️ Estrutura do projeto

```
BackendPromohubs/
├── db/
│   ├── database.py            # Conexão com o PostgreSQL (SQLAlchemy)
│   ├── models.py              # Modelos ORM (tabelas do banco)
│   └── schemas.py             # Schemas Pydantic (validação e serialização)
├── scraping/
│   ├── config.py              # Variáveis de ambiente e grupos monitorados
│   ├── monitor.py             # Monitor de novas mensagens do Telegram (tempo real)
│   ├── scraping-telegram.py   # Coleta o histórico de mensagens dos grupos
│   ├── scraping-kabum.py      # Scraper de ofertas do Kabum (Playwright + BeautifulSoup)
│   ├── scraping-steam.py      # Scraper de promoções da Steam (Playwright)
│   └── utils.py               # Extração e limpeza de texto das mensagens
├── main.py                    # Aplicação FastAPI e definição das rotas
├── requirements.txt
└── LICENSE
```

## 🛠️ Tecnologias utilizadas

- [Python 3](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/) + [PostgreSQL](https://www.postgresql.org/) (via `psycopg2`)
- [Pydantic](https://docs.pydantic.dev/)
- [Telethon](https://docs.telethon.dev/) — integração com a API do Telegram
- [Playwright](https://playwright.dev/python/) — automação de navegador para scraping
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — parsing de HTML
- `aiohttp` / `requests` — requisições HTTP (assíncronas e síncronas)
- `python-dotenv` — carregamento de variáveis de ambiente

## ✅ Pré-requisitos

- Python 3.11 ou superior
- Instância do PostgreSQL em execução
- Credenciais de API do Telegram (`API_ID` e `API_HASH`), obtidas em [my.telegram.org](https://my.telegram.org)
- Navegadores do Playwright instalados (necessário para os scrapers do Kabum e da Steam)

## 🚀 Instalação

**1. Clone o repositório**
```bash
git clone https://github.com/<seu-usuario>/BackendPromohubs.git
cd BackendPromohubs
```

**2. Crie e ative um ambiente virtual**
```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Instale os navegadores do Playwright**
```bash
playwright install chromium
```

**5. Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto (veja a seção [Variáveis de ambiente](#-variáveis-de-ambiente)).

**6. Inicie a API**
```bash
uvicorn main:app --reload
```

A API sobe em `http://localhost:8000` e a documentação interativa (Swagger UI), gerada automaticamente pelo FastAPI, fica disponível em `http://localhost:8000/docs`.

> As tabelas do banco são criadas automaticamente na inicialização, a partir dos modelos definidos em `db/models.py`.

## 🔑 Variáveis de ambiente

| Variável | Descrição |
|---|---|
| `user` | Usuário do banco PostgreSQL |
| `password` | Senha do banco PostgreSQL |
| `database` | Nome do banco de dados |
| `host` | Host do banco de dados |
| `port` | Porta do banco de dados |
| `API_ID` | ID de aplicação do Telegram (my.telegram.org) |
| `API_HASH` | Hash de aplicação do Telegram (my.telegram.org) |
| `API_URL` | URL base da API (ex.: `http://localhost:8000`), usada pelos scrapers para enviar os dados coletados |
| `TOKEN` | Reservado para integrações futuras (ex.: bot do Telegram) |
| `CHAT_ID` | Reservado para integrações futuras |
| `STEAM_URL` | URL de busca de promoções da Steam a ser raspada |
| `KABUM_URL` | URL de ofertas do Kabum a ser raspada |

> ⚠️ O arquivo `.env` nunca deve ser versionado — ele já está listado no `.gitignore`.

Os grupos de Telegram monitorados são definidos na lista `GRUPOS`, em `scraping/config.py`.

## 📡 Endpoints da API

### Produtos
| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/produtos` | Cria um novo produto |
| `GET` | `/produtos` | Lista produtos (paginação via `skip`/`limit`) |
| `PUT` | `/produtos/{produto_id}` | Atualiza um produto existente |
| `DELETE` | `/produtos/{produto_id}` | Remove um produto |

### Cupons
| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/cupons` | Cria um novo cupom |
| `GET` | `/cupons` | Lista cupons |
| `PUT` | `/cupons/{cupom_id}` | Atualiza um cupom existente |
| `DELETE` | `/cupons/{cupom_id}` | Remove um cupom |

### Promoções (Steam)
| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/promocoes` | Cria uma nova promoção |
| `GET` | `/promocoes` | Lista promoções |
| `PUT` | `/promocoes/{promocao_id}` | Atualiza uma promoção existente |
| `DELETE` | `/promocoes/{promocao_id}` | Remove uma promoção |

### Ofertas (Kabum)
| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/kabum` | Cria uma nova oferta |
| `GET` | `/kabum` | Lista ofertas |
| `PUT` | `/kabum/{oferta_id}` | Atualiza uma oferta existente |
| `DELETE` | `/kabum/{oferta_id}` | Remove uma oferta específica |
| `DELETE` | `/kabum` | Remove todas as ofertas (usado antes de cada nova raspagem) |

### Notas fiscais
| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/notas-fiscais` | Registra uma nota fiscal |
| `GET` | `/notas-fiscais` | Lista notas fiscais |

## 🤖 Executando os scrapers

Com a API em execução, cada scraper pode ser rodado separadamente (manualmente ou agendado via `cron`/serviço):

```bash
# Scraper do Kabum — roda em loop, buscando novas ofertas a cada 30 minutos
python scraping/scraping-kabum.py

# Scraper de promoções da Steam — execução única
python scraping/scraping-steam.py

# Coleta o histórico recente de mensagens dos grupos do Telegram — execução única
python scraping/scraping-telegram.py

# Monitor em tempo real de novas mensagens nos grupos do Telegram
python -m scraping.monitor
```

> No primeiro uso dos scripts do Telegram, o Telethon solicitará login (número de telefone e código de verificação) e criará um arquivo de sessão local (`*.session`) para as próximas execuções.

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](./LICENSE) para mais detalhes.
