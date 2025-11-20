import pandas as pd
import asyncio
import aiohttp
from collections import Counter
import os

# --- CONFIGURAÇÕES ---
ARQUIVO_CACHE = 'lotofacil_historico.csv'
URL_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/lotofacil/"

# --- 1. MOTOR DE DADOS (ASSÍNCRONO) ---
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
    
    # 1. Verifica arquivo local
    if os.path.exists(ARQUIVO_CACHE):
        try: 
            df_existente = pd.read_csv(ARQUIVO_CACHE)
            if not df_existente.empty:
                ultimo_salvo = df_existente['concurso'].max()
                # --- SEU PRINT SOLICITADO ---
                print(f" > Base local carregada. Último: {ultimo_salvo}")
        except: pass

    # 2. Conecta na Caixa
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(URL_BASE, ssl=False) as resp:
                if resp.status != 200: return df_existente
                ultimo_real = (await resp.json())['numero']
        except: return df_existente

        if ultimo_real <= ultimo_salvo:
            # --- SEU PRINT SOLICITADO ---
            print(" -> Base já está atualizada.")
            return df_existente

        # 3. Baixa se precisar
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

# --- ESTATÍSTICO ---
def gerar_palpite_base(df, ultimos_n):
    if df.empty: return []
    df = df.copy()
    if isinstance(df['dezenas'].iloc[0], str):
        df['dezenas'] = df['dezenas'].apply(lambda x: [int(i) for i in x.split('-')])
    
    todas = [num for sub in df.tail(ultimos_n)['dezenas'] for num in sub]
    counts = Counter(todas)
    
    stats = pd.DataFrame.from_dict(counts, orient='index', columns=['freq']).reindex(range(1,26), fill_value=0)
    stats['z'] = (stats['freq'] - stats['freq'].mean()) / (stats['freq'].std(ddof=0) or 1)
    return sorted(stats.sort_values('z', ascending=False).head(15).index.tolist())

def montar_jogo_hibrido(df, n_curto=10, n_longo=100):
    lista_quente = gerar_palpite_base(df, n_curto)
    lista_solida = gerar_palpite_base(df, n_longo)
    
    final = list(set(lista_quente) & set(lista_solida))
    for n in lista_quente:
        if len(final) >= 15: break
        if n not in final: final.append(n)
    return sorted(final[:15])

# --- MAIN ---
def main():
    df = asyncio.run(atualizar_base_dados())
    if df.empty: return print("Erro: Base vazia.")

    # --- PAINEL DE CONTROLE ---
    JANELA_CURTA = 10   
    JANELA_LONGA = 100   
    # --------------------------

    # 1. Gera o Palpite Híbrido (Usando as variáveis acima)
    palpite = montar_jogo_hibrido(df, n_curto=JANELA_CURTA, n_longo=JANELA_LONGA)
    
    # 2. Pega o Último Resultado Real
    ultimo_jogo = df.iloc[-1]
    dezenas_reais = [int(x) for x in str(ultimo_jogo['dezenas']).split('-')]
    
    # 3. Verifica
    acertos = len(set(palpite) & set(dezenas_reais))
    
    msg = "Sem prêmio"
    if acertos >= 15: 
        msg = "🚨 15 PONTOS (MÁXIMO)!"
    elif acertos == 14: 
        msg = "💰 14 PONTOS!"
    elif acertos >= 11: 
        msg = f"✅ {acertos} PONTOS (PREMIADO)"
    else: 
        msg = f"❌ {acertos} acertos"

    print("\n" + "="*40)
    print(f"🍀 SEU PALPITE ESTRATÉGICO:")
    print(f"{palpite}")
    print("-" * 40)
    print(f"🔍 CONFERÊNCIA NO ÚLTIMO CONCURSO ({ultimo_jogo['concurso']}):")
    print(f"Resultado: {msg}")
    print("="*40)

if __name__ == "__main__":
    main()