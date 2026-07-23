from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from typing import Optional
  
class Produto(BaseModel):
  nome: str
  preco: Optional[Decimal] = None
  preco_parcelado: Optional[Decimal] = None
  link: Optional[str] = None
  cupom: Optional[str] = None
  imagem: Optional[str] = None
  publicado: bool = True
  
class Cupom(BaseModel):
  nome: str
  codigo: Optional[str] = None
  desconto: Optional[str] = None
  limite_minimo: Optional[Decimal] = None
  link: Optional[str] = None
  imagem: Optional[str] = None
  publicado: bool = True

class PromocaoSteam(BaseModel):
  nome: str
  desconto: Optional[str] = None
  preco_original: Optional[Decimal] = None
  preco_final: Optional[Decimal] = None
  link: Optional[str] = None
  imagem: Optional[str] = None
  publicado: bool = True
  
class NotaFiscal(BaseModel):
  telegram_user_id: int
  telegram_username: Optional[str] = None
  valor_total: Optional[str] = None
  texto_extraido: Optional[str] = None

class ProdutoResponse(Produto):
  id: int
  model_config = ConfigDict(from_attributes=True)

class CupomResponse(Cupom):
  id: int
  model_config = ConfigDict(from_attributes=True)
  
class PromocaoSteamResponse(PromocaoSteam):
  id: int
  model_config = ConfigDict(from_attributes=True)