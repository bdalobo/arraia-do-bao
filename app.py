import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# 1. Configuração visual da página do Arraiá
st.set_page_config(page_title="2º Edição Arraiá do Bão", page_icon="🌽")

st.title("🌽 2º Edição Arraiá do Bão 🔥")
st.write("Escolha o que você vai trazer para a nossa festa no dia 18 de Julho de 2026! Coloque seu nome na opção desejada.")

# 2. SEU CARDÁPIO ORIGINAL
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
    "Maçã do amor", "Algodão doce", "Arroz doce", "Palha Italiana"
]

# 3. Conectando com a sua planilha do Google (Zerar o cache com ttl=0)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    dados_existentes = conn.read(ttl=0)
except Exception as e:
    dados_existentes = pd.DataFrame(columns=["Nome", "WhatsApp", "Comida"])

# 4. SISTEMA DE BLOQUEIO INDEPENDENTE
if not dados_existentes.empty and "Comida" in dados_existentes.columns:
    comidas_ocupadas = [
        c.strip() for c in dados_existentes["Comida"].dropna().astype(str) 
        if c.strip().lower() != "outros"
    ]
else:
    comidas_ocupadas = []

salgados_disponiveis = [c for c in comidas_salgadas if c.strip() not in comidas_ocupadas] + ["Outros"]
doces_disponiveis = [c for c in comidas_doces if c.strip() not in comidas_ocupadas] + ["Outros"]

# 5. Escolha da categoria original fora do formulário
categoria = st.radio("O que você vai trazer?", ["Quero trazer um Salgado", "Quero trazer um Doce"])

comida_final = None

# Criamos o formulário original idêntico ao seu
with st.form("form_arraia", clear_on_submit=True):
    nome = st.text_input("Seu Nome Completo:")
    whatsapp = st.text_input("Seu WhatsApp com DDD (apenas números, ex: 21999999999):")
    
    if categoria == "Quero trazer um Salgado":
        escolha_lista = st.selectbox("Escolha o seu prato Salgado:", salgados_disponiveis, key="sb_salgado")
        if escolha_lista == "Outros":
            outro_prato = st.text_input("Escreva aqui qual SALGADO diferente você vai trazer (Obrigatório):")
            comida_final = outro_prato
        else:
            comida_final = escolha_lista
            
    elif categoria == "Quero trazer um Doce":
        escolha_lista = st.selectbox("Escolha o seu prato Doce:", doces_disponiveis, key="sb_doce")
        if escolha_lista == "Outros":
            outro_prato = st.text_input("Escreva aqui qual DOCE diferente você vai trazer (Obrigatório):")
            comida_final = outro_prato
        else:
            comida_final = escolha_lista
    
    enviado = st.form_submit_button("Confirmar Prato ✨")

# 6. O que acontece quando clica em confirmar
if enviado:
    if nome and whatsapp and comida_final and comida_final.strip():
        if comida_final.strip().lower() == "outros":
            st.error("Por favor, especifique o nome real do prato que você vai trazer.")
        else:
            whatsapp_limpo = "".join(filter(str.isdigit, whatsapp))
            comida_salvar = comida_final.strip()
            
            nova_linha = pd.DataFrame([{"Nome": nome, "WhatsApp": whatsapp_limpo, "Comida": comida_salvar}])
            dados_atualizados = pd.concat([dados_existentes, nova_linha], ignore_index=True)
            
            conn.update(data=dados_atualizados)
            
            st.session_state["sucesso_nome"] = nome
            st.session_state["sucesso_comida"] = comida_salvar
            st.session_state["sucesso_whatsapp"] = whatsapp_limpo
            st.session_state["sucesso_categoria"] = "Salgado" if "Salgado" in categoria else "Doce"
            
            st.rerun()
    else:
        st.error("Por favor, preencha todos os campos! Se você selecionou 'Outros', é obrigatório escrever o nome do prato.")

# 7. Exibe a tela de sucesso e o botão do WhatsApp
if "sucesso_nome" in st.session_state:
    s_nome = st.session_state["sucesso_nome"]
    s_comida = st.session_state["sucesso_comida"]
    s_whatsapp = st.session_state["sucesso_whatsapp"]
    s_cat = st.session_state["sucesso_categoria"]
    
    mensagem = f"Olá! 🎉 Vim confirmar minha presença no *2º Edição Arraiá do Bão*!\n\n*Nome:* {s_nome}\n*Meu WhatsApp:* {s_whatsapp}\n*Categoria:* {s_cat}\n*Prato escolhido:* {s_comida}\n\nJá está salvo no sistema! Nos vemos no dia 18 de Julho! 🌽🔥"
    
    texto_codificado = urllib.parse.quote(mensagem)
    link_whatsapp = f"
