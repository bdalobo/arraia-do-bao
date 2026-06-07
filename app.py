import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# 1. Configuração visual da página do Arraiá
st.set_page_config(page_title="2º Edição Arraiá do Bão", page_icon="🌽")

# 🌟 ESTILIZAÇÃO: Aplicando o SEU novo link de imagem de fundo correto
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://i.ibb.co/6R17stN6/Arraia-do-b-o.png");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    # /* Caixa do formulário com fundo branco semi-transparente para dar excelente leitura */
    [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        padding: 25px !important;
        border-radius: 12px !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    }
    
    # /* Deixa o texto de introdução mais destacado sobre o fundo */
    .stMarkdown p {
        color: #111111;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌽 2º Edição Arraiá do Bão 🔥")
st.write("Escolha o que você vai trazer para a nossa festa no dia 18 de Julho de 2026! Coloque seu nome na opção desejada.")

# 2. SEU CARDÁPIO TOTALMENTE ATUALIZADO
comidas_salgadas = [
    "Cachorro quente", "Cachorro quente de forno", "Pastel de Carne", 
    "Pastel de queijo", "Pastel de calabresa", "Caldo verde", 
    "Sopa de ervilha", "Canjiquinha", "Caldo de pinto", "Caldo de mocotó", 
    "Caldo de feijão", "Salgadinho", "Milho", "Mini pizza", 
    "Torta de frango", "Torta de sardinha", "Empadão de frango", "Pipoca Salgada",
    "Quiche", "Salgadinho assado", "Frios", "Torta salgada", "Cuscuz amarelo"
]

comidas_doces = [
    "Bolo de chocolate", "Bolo de milho", "Bolo de fubá com goiabada", 
    "Bolo de aipim", "Paçoca", "Pé de moleque", "Brigadeiro", 
    "Pipoca doce", "Cuscuz Branco", "Curau", "Canjica", 
    "Maçã do amor", "Algodão doce", "Arroz doce"
]

# 3. Conectando com a sua planilha do Google (Zerar o cache com ttl=0)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    dados_existentes = conn.read(ttl=0)
except Exception as e:
    dados_existentes = pd.DataFrame(columns=["Nome", "WhatsApp", "Comida"])

# 4. SISTEMA DE BLOQUEIO INDEPENDENTE
if not dados_existentes.empty and "Comida" in dados_existentes.columns:
    comidas_ocupadas = dados_existentes["Comida"].dropna().astype(str).str.strip().tolist()
else:
    comidas_ocupadas = []

salgados_disponiveis = [c for c in comidas_salgadas if c.strip() not in comidas_ocupadas] + ["Outros"]
doces_disponiveis = [c for c in comidas_doces if c.strip() not in comidas_ocupadas] + ["Outros"]

# 5. Escolha da categoria FORA do formulário
categoria = st.radio("O que você vai trazer?", ["Quero trazer um Salgado", "Quero trazer um Doce"])

comida_final = None

# Criamos o formulário
with st.form("form_arraia", clear_on_submit=True):
    nome = st.text_input("Seu Nome Completo:")
    whatsapp = st.text_input("Seu WhatsApp com DDD (apenas números, ex: 21999999999):")
    
    if categoria == "Quero trazer um Salgado":
        escolha_lista = st.selectbox("Escolha o seu prato Salgado:", salgados_disponiveis)
        if escolha_lista == "Outros":
            outro_prato = st.text_input("Escreva aqui qual SALGADO diferente você vai trazer (Obrigatório):")
            comida_final = outro_prato
        else:
