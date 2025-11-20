# 🍀 Gerador Lotofácil

> Programa em Python para gerar jogos inteligentes

Este projeto é uma ferramenta de análise estatística e previsão para a Lotofácil, desenvolvida em Python. 
O script utiliza dados históricos oficiais da Caixa Econômica Federal para identificar tendências de curto e longo prazo, aplicando conceitos de **Desvio Padrão (Z-Score)** e **Interseção de Conjuntos**.

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## 🧠 Como Funciona a Estratégia Híbrida

O algoritmo não conta com a sorte; ele conta com dados. A geração do palpite acontece em três etapas:

1.  **Coleta Assíncrona (`asyncio` + `aiohttp`):** O script baixa automaticamente todos os resultados da história da Lotofácil diretamente da API da Caixa. Possui sistema de cache local (`.csv`) para não baixar dados repetidos, garantindo performance máxima.
2.  **Cálculo Z-Score:** Analisa a frequência de cada dezena e normaliza os dados usando Z-Score para encontrar os números com maior desvio estatístico positivo.
3.  **O Cruzamento (Interseção):**
    * **Lista Quente (Curto Prazo):** Analisa a tendência dos últimos **10 concursos**.
    * **Lista Sólida (Longo Prazo):** Analisa a consistência dos últimos **100 concursos**.
    * **Palpite Final:** O jogo é montado priorizando os números que aparecem em **ambas** as listas (Unanimidades), preenchendo o restante com as maiores tendências do momento.

## 🚀 Funcionalidades

- [x] **Download Automático:** Sincronização inteligente com a base de dados oficial.
- [x] **Modo Offline:** Funciona com cache local se a internet cair.
- [x] **Backtest (Máquina do Tempo):** Simula o desempenho da estratégia no concurso anterior antes de gerar o palpite futuro.
- [x] **Performance:** Uso de concorrência para downloads rápidos.

## 🛠️ Instalação e Uso

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU-USUARIO/lotofacil-estrategia.git](https://github.com/SEU-USUARIO/lotofacil-estrategia.git)
   cd lotofacil-estrategia
   
2. **Instale as dependências:**
   pip install pandas aiohttp
   
3. **Execute o programa:**
   python lotofacil_gerador.py

⚠️ **Disclaimer**

Este software é uma ferramenta de estudo estatístico e não garante lucros. 
Loterias são jogos de azar e os resultados passados não garantem resultados futuros. Jogue com responsabilidade.

📝 **Licença**

Este projeto está sob a licença MIT - sinta-se livre para usar e modificar, mantendo os créditos.

Desenvolvido por **Boleto**
