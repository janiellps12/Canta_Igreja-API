import os
from pathlib import Path
from tqdm import tqdm
import pandas as pd


from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v1')

caminho_musicas = Path('../dados/musicas')
caminho_musicas_todo = Path('../dados/musicas2')

arquivos = os.listdir(caminho_musicas)# + os.listdir(caminho_musicas_todo)
arquivos2 = os.listdir(caminho_musicas_todo)
#arquivos = sorted(arquivos)

def ler_arquivo(arquivo: Path):
    texto = arquivo.read_text()
    return texto.split("Cifraclub:")[-1]

def embedding(conteudo: str):
    return model.encode(conteudo.split("Cifraclub:")[-1])

def similares(conteudo, chave: str, top_n=5):
    base = conteudo[chave]

    similares = []
    for key, value in conteudo.items():
        if key != chave:
            similares.append({'reference': chave, 'similar': key, 'similarity': float(util.cos_sim(base, value))})
    
    similares = pd.DataFrame(similares)
    return similares.sort_values('similarity', ascending=False)[:top_n]

conteudo = {}
for nome_arquivo in tqdm(arquivos, desc='Encoding'):
    arquivo = caminho_musicas / nome_arquivo
    conteudo_arquivo = ler_arquivo(arquivo)
    if conteudo_arquivo.strip() != '':
        conteudo[nome_arquivo] = embedding(conteudo_arquivo)

for nome_arquivo in tqdm(arquivos2, desc='Encoding TODO'):
    arquivo = caminho_musicas_todo / nome_arquivo
    conteudo_arquivo = ler_arquivo(arquivo)
    if conteudo_arquivo.strip() != '':
        conteudo[nome_arquivo] = embedding(conteudo_arquivo)

arquivos_similares = []
for arquivo in tqdm(conteudo.keys(), desc='Similarity search'):
    arquivos_similares.append(similares(conteudo, arquivo))

arquivos_similares = pd.concat(arquivos_similares)
arquivos_similares.to_csv('similares.csv')