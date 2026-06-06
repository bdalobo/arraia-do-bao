import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# 1. Configuração visual da página do Arraiá
st.set_page_config(page_title="2º Edição Arraiá do Bão", page_icon="🌽")

st.title("🌽 2º Edição Arraiá do Bão 🔥")
st.write("Escolha o que você vai trazer para a nossa festa no dia 18 de Julho de 2026! Coloque seu nome na opção desejada.")

# 2. SEU CARDÁPIO PRONTO
comidas_salgadas = [
    "Cachorro quente", "Cachorro quente de forno", "Pastel de Carne", 
    "Pastel de queijo", "Pastel de calabresa", "Caldo verde", 
    "Sopa de ervilha", "Canjiquinha", "Caldo de pinto", "Caldo de mocotó", 
    "Caldo de feijão", "Salgadinho", "Milho", "Mini pizza", 
    "Torta de frango", "Torta de sardinha", "Empadão de frango", "Pipoca Salgada"
]

comidas_doces = [
    "Bolo de chocolate", "Bolo de milho", "Bolo de fubá com goiabada", 
    "Bolo de aipim", "Paçoca", "Pé de moleque", "Brigadeiro", 
    "Pipoca doce", "Cuscuz Branco", "Curau", "Canjica", 
    "Maçã do amor", "Algodão doce", "Arroz doce"
]

# 3. Conectando com a sua planilha do Google
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    dados_existentes = conn.read()
except Exception as e:
    dados_existentes = pd.DataFrame(columns=["Nome", "WhatsApp", "Comida"])

# 4. SISTEMA DE BLOQUEIO INDEPENDENTE
if not dados_existentes.empty and "Comida" in dados_existentes.columns:
    comidas_ocupadas = dados_existentes["Comida"].dropna().tolist()
else:
    comidas_ocupadas = []

# Filtra o que já foi escolhido e ADICIONA a opção "Outros" no final
salgados_disponiveis = [c for c in comidas_salgadas if c not in comidas_ocupadas] + ["Outros"]
doces_disponiveis = [c for c in comidas_doces if c not in comidas_ocupadas] + ["Outros"]

# 5. Escolha da categoria fora do formulário (para atualizar na hora!)
categoria = st.radio("O que você vai trazer?", ["Quero trazer um Salgado", "Quero trazer um Doce"])

comida_final = None

# Formulário principal
with st.form("form_arraia", clear_on_submit=True):
    nome = st.text_input("Seu Nome Completo:")
    whatsapp = st.text_input("Seu WhatsApp com DDD (apenas números, ex: 21999999999):")
    
    # Se escolheu Salgado
    if categoria == "Quero trazer um Salgado":
        escolha_lista = st.selectbox("Escolha o seu prato Salgado:", salgados_disponiveis)
        # Se escolheu "Outros", abre a caixinha de texto obrigatória
        if escolha_lista == "Outros":
            outro_prato = st.text_input("Escreva aqui qual SALGADO diferente você vai trazer:")
            comida_final = outro_prato
        else:
            comida_final = escolha_lista
            
    # Se escolheu Doce
    elif categoria == "Quero trazer um Doce":
        escolha_lista = st.selectbox("Escolha o seu prato Doce:", doces_disponiveis)
        # Se escolheu "Outros", abre a caixinha de texto obrigatória
        if escolha_lista == "Outros":
            outro_prato = st.text_input("Escreva aqui qual DOCE diferente você vai trazer:")
            comida_final = outro_prato
        else:
            comida_final = escolha_lista
            
    enviado = st.form_submit_button("Confirmar Prato ✨")

# 6. Processamento do envio
if enviado:
    # Verifica se digitou nome, whatsapp e se a comida final não está em branco
    if nome and whatsapp and comida_final and comida_final.strip():
        whatsapp_limpo = "".join(filter(str.isdigit, whatsapp))
        comida_salvar = comida_final.strip()
        
        # Salva na planilha do Google
        nova_linha = pd.DataFrame([{"Nome": nome, "WhatsApp": whatsapp_limpo, "Comida": comida_salvar}])
        dados_atualizados = pd.concat([dados_existentes, nova_linha], ignore_index=True)
        conn.update(data=dados_atualizados)
        
        # Cria o link do seu WhatsApp
        tipo_comida = "Salgado" if "Salgado" in categoria else "Doce"
        mensagem = (
            f"Olá! 🎉 Vim confirmar minha presença no *2º Edição Arraiá do Bão*!\n\n"
            f"*Nome:* {nome}\n"
            f"*Meu WhatsApp:* {whatsapp_limpo}\n"
            f"*Categoria:* {tipo_comida}\n"
            f"*Prato escolhido:* {comida_salvar}\n\n"
            f"Já está salvo no sistema! Nos vemos no dia 18 de Julho! 🌽🔥"
        )
        
        texto_codificado = urllib.parse.quote(mensagem)
        link_whatsapp = f"https://api.whatsapp.com/send?phone=5521999161661&text={texto_codificado}"
        
        st.success(f"Sucesso, {nome}! Seu prato (*{comida_salvar}*) foi reservado.")
        st.write("📢 **ÚLTIMO PASSO OBRIGATÓRIO:** Clique no botão abaixo para me enviar sua confirmação direto no meu WhatsApp!")
        
        st.link_button("👉 Enviar Confirmação no WhatsApp da Organizadora", link_whatsapp)
    else:
        st.error("Por favor, preencha todos os campos! Se escolheu 'Outros', você precisa digitar o nome do prato.")
