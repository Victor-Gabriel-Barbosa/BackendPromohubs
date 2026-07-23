from sqlalchemy import Column, Integer, Numeric, Boolean, String, TIMESTAMP, BigInteger, DateTime
from sqlalchemy.sql import text
from datetime import datetime, timezone
from db.database import Base

DEFAULT_TIMESTAMP = text('now()')
  
class Produto(Base):
  __tablename__ = "produto"
  id = Column(Integer, primary_key=True, nullable=False)
  nome = Column(String, nullable=True)
  preco = Column(Numeric(10, 2), nullable=True)
  preco_parcelado = Column(Numeric(10, 2), nullable=True)
  link = Column(String, nullable=True)
  cupom = Column(String, nullable=True)
  imagem = Column(String, nullable=True)
  publicado = Column(Boolean, server_default='True', nullable=False)
  created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=DEFAULT_TIMESTAMP)
  
class Cupom(Base):
  __tablename__ = "cupom"
  id = Column(Integer, primary_key=True, nullable=False)
  nome = Column(String, nullable=True)
  codigo = Column(String, nullable=True)
  desconto = Column(String, nullable=True)
  limite_minimo = Column(Numeric(10, 2), nullable=True)
  link = Column(String, nullable=True)
  imagem = Column(String, nullable=True)
  publicado = Column(Boolean, server_default='True', nullable=False)
  created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=DEFAULT_TIMESTAMP)
  
class PromocaoSteam(Base):
  __tablename__ = "promocao_steam"
  id = Column(Integer, primary_key=True, nullable=False)
  nome = Column(String, nullable=True)
  desconto = Column(String, nullable=True)
  preco_original = Column(Numeric(10, 2), nullable=True)
  preco_final = Column(Numeric(10, 2), nullable=True)
  link = Column(String, nullable=True)
  imagem = Column(String, nullable=True)
  publicado = Column(Boolean, server_default='True', nullable=False)
  created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=DEFAULT_TIMESTAMP)

class NotaFiscal(Base):
  __tablename__ = "notas_fiscais"
  id = Column(Integer, primary_key=True, index=True)
  telegram_user_id = Column(BigInteger, nullable=False)
  telegram_username = Column(String, nullable=True)
  valor_total = Column(String, nullable=True)
  texto_extraido = Column(String, nullable=True)
  created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
  
class OfertaKabum(Base):
  __tablename__ = "oferta_kabum"
  id = Column(Integer, primary_key=True, nullable=False)
  nome = Column(String, nullable=True)
  preco = Column(Numeric(10, 2), nullable=True)
  desconto = Column(String, nullable=True)
  link = Column(String, nullable=True)
  imagem = Column(String, nullable=True)
  publicado = Column(Boolean, server_default='True', nullable=False)
  created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=DEFAULT_TIMESTAMP)