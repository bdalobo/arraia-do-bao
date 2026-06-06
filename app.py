import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# Configuração da página do Arraiá
st.set_page_config(page_title="2º Edição Arraiá do Bão", page_icon="🌽")

st.title("🌽 2º Edição Arraiá do Bão 🔥")
st.write("Escolha o que você vai trazer para a nossa festa no dia 18 de Julho de 2026! Coloque seu nome na opção desejada.")

# LISTA DE COMIDAS (Você pode alterar os nomes aqui se quiser!)
todas_comidas = [
    "Bolo de Fubá", "Canjica", "Pipoca", "Pamonha", "Quentão", 
    "Caldo Verde", "Cachorro Quente", "Salgadinhos", "Doces Juninos", 
    "Milho Cozido", "Bolo de Aipim", "Arroz Doce"
]

# Conectando com a planilha do Google
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    dados_existentes = conn.read()
except Exception as e:
    dados_existentes = pd.DataFrame(columns=["Nome", "WhatsApp", "Comida"])

# Descobrir quais comidas já foram escolhidas
if not dados_existentes.empty and "Comida" in dados_existentes.columns:
    comidas_ocupadas = dados_existentes["Comida"].dropna().tolist()
else:
    comidas_ocupadas = []

# Filtrar para mostrar apenas as comidas que estão livres
comidas_disponiveis = [c for c in todas_comidas if c not in comidas_ocupadas]

# Formulário na Tela
if len(comidas_disponiveis) == 0:
    st.warning("Eita! Todas as comidas já foram escolhidas! 🎉")
else:
    with st.form("form_arraia", clear_on_submit=True):
        nome = st.text_input("Seu Nome Completo:")
        whatsapp = st.text_input("Seu WhatsApp com DDD (apenas números, ex: 21999999999):")
        comida_escolhida = st.selectbox("Escolha o seu prato:", comidas_disponiveis)
        
        enviado = st.form_submit_button("Confirmar Prato ✨")

    if enviado:
        if nome and whatsapp and comida_escolhida:
            # Preparando a nova linha para salvar na planilha
            nova_linha = pd.DataFrame([{"Nome": nome, "WhatsApp": whatsapp, "Comida": comida_escolhida}])
            dados_atualizados = pd.concat([dados_existentes, nova_linha], ignore_index=True)
            
            # Atualiza a planilha do Google
            conn.update(data=dados_atualizados)
            
            # Criando a mensagem de WhatsApp
            mensagem = f"Olá! 🎉 Confirmação automática do *2º Edição Arraiá do Bão*!\n\n*Nome:* {nome}\n*Prato escolhido:* {comida_escolhida}\n\nSua escolha foi salva! Nos vemos no dia 18 de Julho! 🌽🔥"
            texto_codificado = urllib.parse.quote(mensagem)
            
            # Monta o link para o WhatsApp do próprio convidado
            link_whatsapp = f"https://api.whatsapp.com/send?phone=55{whatsapp}&text={texto_codificado}"
            
            st.success(f"Sucesso, {nome}! Seu prato foi reservado.")
            st.write("📢 **ÚLTIMO PASSO:** Clique no botão abaixo para abrir seu WhatsApp e receber sua confirmação oficial!")
            st.link_button("👉 Abrir WhatsApp para Confirmar", link_whatsapp)
            
            # Força o site a atualizar para sumir com a comida da lista
            st.rerun()
        else:
            st.error("Por favor, preencha todos os campos antes de confirmar!")
