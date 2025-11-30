import pandas as pd
import asyncio
import aiohttp
from collections import Counter
import os
import itertools
import random

# --- CONFIGURAÇÕES ---
ARQUIVO_CACHE = 'lotofacil_historico.csv'
URL_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"

# Constantes Matemáticas da Lotofácil
PRIMOS = {2, 3, 5, 7, 11, 13, 17, 19, 23}
FIBONACCI = {1, 2, 3, 5, 8, 13, 21}

# --- 1. MOTOR DE DADOS (MANTIDO IGUAL) ---
async def buscar_concurso(session, numero):
    try:
        async with session.get(f"{URL_BASE}{numero}", ssl=False) as response:
            if response.status == 200:
                d = await response.json()
                return {'concurso': d['numero'], 'dezenas': [int(x) for x in d['listaDezenas']]}
    except: pass
    return None

async def atualizar_base_dados():
    df_existente = pd.DataFrame(columns=['concurso', 'dezenas'])
    ultimo_salvo = 0
    
    if os.path.exists(ARQUIVO_CACHE):
        try: 
            df_existente = pd.read_csv(ARQUIVO_CACHE)
            if not df_existente.empty:
                ultimo_salvo = df_existente['concurso'].max()
                print(f" > Base local carregada. Último: {ultimo_salvo}")
        except: pass

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(URL_BASE, ssl=False) as resp:
                if resp.status != 200: return df_existente
                ultimo_real = (await resp.json())['numero']
        except: return df_existente
            
        if ultimo_real <= ultimo_salvo:
            print(" -> Base já está atualizada.")
            return df_existente

        tarefas = [buscar_concurso(session, n) for n in range(ultimo_salvo + 1, ultimo_real + 1)]
        novos = await asyncio.gather(*tarefas)
        novos = [n for n in novos if n]

    if novos:
        df_novos = pd.DataFrame(novos)
        df_novos['dezenas'] = df_novos['dezenas'].apply(lambda x: '-'.join(map(str, x)))
        df_final = pd.concat([df_existente, df_novos]).sort_values('concurso')
        df_final.to_csv(ARQUIVO_CACHE, index=False)
        print(f" -> Base atualizada com sucesso! Novos: {len(novos)}")
        return df_final
        
    return df_existente

# --- 2. CÉREBRO ESTATÍSTICO (NOVO) ---
class FiltrosAvancados:
    @staticmethod
    def validar(jogo, repetentes_concurso_anterior):
        # 1. Filtro de Pares (Padrão: 6 a 9 pares)
        pares = len([x for x in jogo if x % 2 == 0])
        if not (6 <= pares <= 9): return False, "Falha Pares"

        # 2. Filtro de Primos (Padrão: 4 a 6 primos)
        primos = len([x for x in jogo if x in PRIMOS])
        if not (3 <= primos <= 7): return False, "Falha Primos"

        # 3. Soma Total (Curva de Gauss: 180 a 230)
        soma = sum(jogo)
        if not (180 <= soma <= 230): return False, "Falha Soma"

        # 4. Repetentes do Anterior (Padrão: 8 a 10)
        # Se não tiver dados do anterior, ignora
        if repetentes_concurso_anterior:
            reps = len(set(jogo) & set(repetentes_concurso_anterior))
            if not (7 <= reps <= 11): return False, "Falha Repetentes"

        return True, "OK"

def gerar_ranking_z(df, janela):
    """Gera um ranking dos números baseado no Z-Score (Desvio Padrão)"""
    if df.empty: return []
    df = df.copy()
    if isinstance(df['dezenas'].iloc[0], str):
        df['dezenas'] = df['dezenas'].apply(lambda x: [int(i) for i in x.split('-')])
    
    todas = [num for sub in df.tail(janela)['dezenas'] for num in sub]
    counts = Counter(todas)
    
    stats = pd.DataFrame.from_dict(counts, orient='index', columns=['freq']).reindex(range(1,26), fill_value=0)
    # Z-Score: Quão longe da média está a frequência desse número?
    stats['z'] = (stats['freq'] - stats['freq'].mean()) / (stats['freq'].std(ddof=0) or 1)
    return stats.sort_values('z', ascending=False)

def gerar_jogo_inteligente(df, n_curto=15, n_longo=100):
    # 1. Analisa o último jogo para filtro de repetentes
    ultimo_concurso = df.iloc[-1]
    dezenas_anterior = [int(x) for x in str(ultimo_concurso['dezenas']).split('-')]

    # 2. Pega os melhores números (Pool de Candidatos)
    # Em vez de pegar só os 15 melhores, pegamos os 21 melhores para criar variações
    rank_curto = gerar_ranking_z(df, n_curto)
    rank_longo = gerar_ranking_z(df, n_longo)
    
    # Peso 70% curto prazo, 30% longo prazo
    rank_final = (rank_curto['z'] * 0.7) + (rank_longo['z'] * 0.3)
    top_candidatos = rank_final.sort_values(ascending=False).head(21).index.tolist()
    
    print(f"Pool de números quentes (Top 21): {top_candidatos}")
    
    # 3. Força Bruta Inteligente: Testa combinações dentro dos números quentes
    # Gerar combinações de 15 dentro dos 21 quentes (aprox 54.000 combinações - rápido p/ PC)
    melhor_jogo = []
    melhor_score = -999
    
    # Limitamos a tentativas aleatórias para não travar se o pool for gigante, 
    # ou usamos itertools para precisão
    tentativas = itertools.combinations(top_candidatos, 15)
    
    count_validos = 0
    
    for comb in tentativas:
        jogo = sorted(list(comb))
        
        # Passa pelos filtros rigorosos
        valido, motivo = FiltrosAvancados.validar(jogo, dezenas_anterior)
        
        if valido:
            count_validos += 1
            # Se passou nos filtros, pontua pelo Z-Score total
            score_atual = sum([rank_final.loc[n] for n in jogo])
            
            if score_atual > melhor_score:
                melhor_score = score_atual
                melhor_jogo = jogo
    
    print(f"Combinações analisadas matematicamente dentro do Pool: {count_validos} válidas encontradas.")
    return melhor_jogo if melhor_jogo else top_candidatos[:15]

# --- MAIN ---
def main():
    print("--- INICIANDO SISTEMA QUANTITATIVO LOTOFÁCIL ---")
    df = asyncio.run(atualizar_base_dados())
    if df.empty: return print("Erro: Base vazia.")

    # --- SIMULAÇÃO ---
    # Para testar, vamos "esconder" o último resultado real e tentar prever ele
    # Na vida real, você usaria o DF completo para prever o FUTURO.
    
    # df_treino = df.iloc[:-1] # Descomente para testar backtest (prever o passado)
    df_treino = df # Use o DF completo para prever o próximo jogo real

    JANELA_CURTA = 10    
    JANELA_LONGA = 100    

    palpite = gerar_jogo_inteligente(df_treino, n_curto=JANELA_CURTA, n_longo=JANELA_LONGA)
    
    # Análise Estatística do Palpite Final
    pares = len([x for x in palpite if x % 2 == 0])
    soma = sum(palpite)
    primos = len([x for x in palpite if x in PRIMOS])
    
    print("\n" + "="*40)
    print(f"🍀 SEU PALPITE MATEMÁTICO (FILTRADO):")
    print(f"{palpite}")
    print("-" * 40)
    print(f"📊 DNA do Jogo:")
    print(f" > Soma: {soma} (Meta: 180-230)")
    print(f" > Pares: {pares} (Meta: 6-9)")
    print(f" > Primos: {primos} (Meta: 3-7)")
    print("="*40)

    # Conferência com o último real (apenas se estivermos fazendo backtest)
    # ultimo_real = [int(x) for x in str(df.iloc[-1]['dezenas']).split('-')]
    # acertos = len(set(palpite) & set(ultimo_real))
    # print(f"Se fosse no último concurso: {acertos} acertos")

if __name__ == "__main__":
    main()
