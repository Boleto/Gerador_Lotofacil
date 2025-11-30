# 🍀 Gerador Lotofácil 

> Programa em Python para gerar jogos inteligentes

> *"Aqueles que planejam com antecedência vencem a batalha antes mesmo de ela começar."*

Este é o módulo de **Análise Quantitativa Avançada** para a Lotofácil. Diferente de geradores aleatórios ou baseados apenas em frequência simples, este algoritmo aplica conceitos de **Data Science**, **Combinatória** e **Filtragem Estatística** para encontrar o jogo matematicamente ideal.

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Analytics-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Itertools](https://img.shields.io/badge/Lib-Itertools-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## A Arquitetura do Algoritmo

O script não busca apenas os números que mais saem. Ele busca a **estrutura ideal** de um jogo vencedor através de 4 etapas rigorosas:

### 1. Z-Score Ponderado (Weighted Scoring)
O algoritmo calcula o Desvio Padrão (Z-Score) de cada dezena em duas janelas temporais, atribuindo pesos diferentes:
* **70% de Peso:** Tendência de Curto Prazo (Últimos 10 concursos).
* **30% de Peso:** Consistência Histórica (Últimos 100 concursos).

### 2. O "Pool" de Candidatos (Expansão)
Ao invés de fechar o jogo com os Top 15 números (o que seria simplista), o algoritmo seleciona os **Top 21 Candidatos** com melhor pontuação estatística. Isso cria uma margem de segurança para capturar dezenas que oscilam.

### 3. Força Bruta Inteligente (Combinatória)
Utilizando a biblioteca `itertools`, o sistema gera todas as combinações possíveis de 15 números dentro do grupo de 21 candidatos (aprox. 54.000 combinações).

### 4. O Funil de Filtros (Validação)
Cada uma das combinações geradas passa por um "crivo" rigoroso. Só é aprovado o jogo que respeitar as leis da probabilidade da Lotofácil:
* ✅ **Soma Total:** Deve estar na Curva de Gauss (entre 180 e 230).
* ✅ **Pares/Ímpares:** Deve manter o equilíbrio (entre 6 e 9 pares).
* ✅ **Números Primos:** Deve conter a quantidade padrão (entre 3 e 7 primos).
* ✅ **Repetentes:** Deve respeitar o ciclo do concurso anterior (entre 7 e 11 repetidas).

---

## 🚀 Funcionalidades Técnicas

- [x] **Motor Assíncrono:** Download ultra-rápido da base de dados oficial da Caixa via `aiohttp`.
- [x] **Cache Inteligente:** Sistema de armazenamento local (`.csv`) para operação offline.
- [x] **Filtros Dinâmicos:** Classes dedicadas para validação matemática de jogos.
- [x] **Previsão Futura:** Configurado para projetar o próximo concurso com base em dados reais atualizados.

---

## 🛠️ Instalação e Uso

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/Boleto/Gerador_Lotofacil.git
   ```
2. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Execute o programa:**
   ```bash
   python lotofacil_gerador.py
   ```
   
⚠️ **Disclaimer**

Este software é uma ferramenta de estudo estatístico e não garante lucros. 
Loterias são jogos de azar e os resultados passados não garantem resultados futuros. Jogue com responsabilidade.

📝 **Licença**

Este projeto está sob a licença MIT - sinta-se livre para usar e modificar, mantendo os créditos.

---
Desenvolvido por **Boleto**<br>
*AI Assistance: Google Gemini*


