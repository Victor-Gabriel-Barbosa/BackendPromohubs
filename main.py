from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status, Depends, HTTPException, Response
from db.schemas import Produto, Cupom, PromocaoSteam, NotaFiscal, OfertaKabum, ProdutoResponse, CupomResponse, PromocaoSteamResponse, NotaFiscalResponse, OfertaKabumResponse
from db import models
from db.database import engine, get_db
from sqlalchemy.orm import Session
from typing import List

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ['http://localhost:3000']

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*']
)
 
@app.post("/produtos", status_code=status.HTTP_201_CREATED)
async def criar_produto(produto: Produto, db: Session = Depends(get_db)):
  novo_produto = models.produto(**produto.model_dump())
  db.add(novo_produto)
  db.commit()
  db.refresh(novo_produto)
  print(produto)
  return {"Produto": novo_produto}

@app.post("/cupons", status_code=status.HTTP_201_CREATED)
async def criar_cupom(cupom: Cupom, db: Session = Depends(get_db)):
  novo_cupom = models.cupom(**cupom.model_dump())
  db.add(novo_cupom)
  db.commit()
  db.refresh(novo_cupom)
  print(cupom)
  return {"Cupom": novo_cupom}

@app.get("/produtos", response_model=List[ProdutoResponse], status_code=status.HTTP_200_OK)
async def buscar_produtos(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
  return db.query(models.produto).offset(skip).limit(limit).all()

@app.get("/cupons", response_model=List[CupomResponse], status_code=status.HTTP_200_OK)
async def buscar_cupons(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
  return db.query(models.cupom).offset(skip).limit(limit).all()

@app.put("/produtos/{produto_id}", response_model=ProdutoResponse, status_code=status.HTTP_200_OK)
async def atualizar_produto(produto_id: int, produto: Produto, db: Session = Depends(get_db)):
  produto_query = db.query(models.produto).filter(models.produto.id == produto_id)
  produto_existente = produto_query.first()
  if produto_existente is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
  produto_query.update(produto.model_dump(), synchronize_session=False)
  db.commit()
  return produto_query.first()

@app.put("/cupons/{cupom_id}", response_model=CupomResponse, status_code=status.HTTP_200_OK)
async def atualizar_cupom(cupom_id: int, cupom: Cupom, db: Session = Depends(get_db)):
  cupom_query = db.query(models.cupom).filter(models.cupom.id == cupom_id)
  cupom_existente = cupom_query.first()
  if cupom_existente is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cupom não encontrado")
  cupom_query.update(cupom.model_dump(), synchronize_session=False)
  db.commit()
  return cupom_query.first()
  
@app.delete("/produtos/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_produto(produto_id: int, db: Session = Depends(get_db)):
  produto_query = db.query(models.produto).filter(models.produto.id == produto_id)
  if produto_query.first() is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
  produto_query.delete(synchronize_session=False)
  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.delete("/cupons/{cupom_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_cupom(cupom_id: int, db: Session = Depends(get_db)):
  cupom_query = db.query(models.cupom).filter(models.cupom.id == cupom_id)
  if cupom_query.first() is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cupom não encontrado")
  cupom_query.delete(synchronize_session=False)
  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/promocoes", status_code=status.HTTP_201_CREATED)
async def criar_promocao(promocao: PromocaoSteam, db: Session = Depends(get_db)):
  nova_promocao = models.promocao_steam(**promocao.model_dump())
  db.add(nova_promocao)
  db.commit()
  db.refresh(nova_promocao)
  print(promocao)
  return {"PromocaoSteam": nova_promocao}

@app.get("/promocoes", response_model=List[PromocaoSteamResponse], status_code=status.HTTP_200_OK)
async def buscar_promocoes(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
  return db.query(models.promocao_steam).offset(skip).limit(limit).all()

@app.put("/promocoes/{promocao_id}", response_model=PromocaoSteamResponse, status_code=status.HTTP_200_OK)
async def atualizar_promocao(promocao_id: int, promocao: PromocaoSteam, db: Session = Depends(get_db)):
  promocao_query = db.query(models.promocao_steam).filter(models.promocao_steam.id == promocao_id)
  promocao_existente = promocao_query.first()
  if promocao_existente is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promoção não encontrada")      
  promocao_query.update(promocao.model_dump(), synchronize_session=False)
  db.commit()
  return promocao_query.first()

@app.delete("/promocoes/{promocao_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remover_promocao(promocao_id: int, db: Session = Depends(get_db)):
  promocao_query = db.query(models.promocao_steam).filter(models.promocao_steam.id == promocao_id)
  if promocao_query.first() is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Promoção não encontrada")
  promocao_query.delete(synchronize_session=False)
  db.commit()
  return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/notas-fiscais", status_code=status.HTTP_201_CREATED)
async def criar_nota_fiscal(nota_fiscal: NotaFiscal, db: Session = Depends(get_db)):
  nova_nota_fiscal = models.NotaFiscal(**nota_fiscal.model_dump())
  db.add(nova_nota_fiscal)
  db.commit()
  db.refresh(nova_nota_fiscal)
  print(nota_fiscal)
  return {"NotaFiscal": nova_nota_fiscal}

@app.get("/notas-fiscais", response_model=List[NotaFiscalResponse], status_code=status.HTTP_200_OK)
async def buscar_notas_fiscais(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
  return db.query(models.NotaFiscal).offset(skip).limit(limit).all()

@app.post("/ofertas-kabum", status_code=status.HTTP_201_CREATED)
async def criar_oferta_kabum(oferta: OfertaKabum, db: Session = Depends(get_db)):
  nova_oferta = models.OfertaKabum(**oferta.model_dump())
  db.add(nova_oferta)
  db.commit()
  db.refresh(nova_oferta)
  return {"OfertaKabum": nova_oferta}

@app.get("/ofertas-kabum", response_model=List[OfertaKabumResponse], status_code=status.HTTP_200_OK)
async def buscar_ofertas_kabum(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
  return db.query(models.OfertaKabum).offset(skip).limit(limit).all()