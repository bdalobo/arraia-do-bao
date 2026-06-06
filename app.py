import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# 1. Configuração visual da página do Arraiá
st.set_page_config(page_title="2º Edição Arraiá do Bão", page_icon="🌽")

st.title("🌽 2º Edição Arraiá do Bão 🔥")
st.write("Escolha o que você vai trazer para a nossa festa no dia 18 de Julho de 2026! Coloque seu nome na opção desejada.")

# 2. SEU CARDÁPIO TOTALMENTE SEPARADO
comidas_salgadas = [
    "Cachorro quente", "Cachorro quente de forno", "Pastel de Carne", 
    "Pastel de queijo", "Pastel de calabresa", "Caldo verde", 
    "Sopa de ervilha", "Canjiquinha", "Caldo de pinto", "Caldo de mocotó", 
    "Caldo de feijão", "Salgadinho", "Milho", "Mini pizza", 
    "Torta de frango", "Torta de sardinha", "Empadão de frango", "Pipoca Salgada", "Outros"
]

comidas_doces = [
    "Bolo de chocolate", "Bolo de milho", "Bolo de fubá com goiabada", 
    "Bolo de aipim", "Paçoca", "Pé de moleque", "Brigadeiro", 
    "Pipoca doce", "Cuscuz Branco", "Curau", "Canjica", 
    "Maçã do amor", "Algodão doce", "Arroz doce", "Outros"
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

# Filtra cada lista na sua própria caixinha
salgados_disponiveis = [c for c in comidas_salgadas if c not in comidas_ocupadas]
doces_disponiveis = [c for c in comidas_doces if c not in comidas_ocupadas]

# --- ADENDO DE ATUALIZAÇÃO EM TEMPO REAL ---
# Colocamos a escolha da categoria FORA do formulário para o site atualizar na hora do clique!
categoria = st.radio("O que você vai trazer?", ["Quero trazer um Salgado", "Quero trazer um Doce"])

comida_escolhida = None

# Criamos o formulário apenas para os dados e o prato
with st.form("form_arraia", clear_on_submit=True):
    nome = st.text_input("Seu Nome Completo:")
    whatsapp = st.text_input("Seu WhatsApp com DDD (apenas números, ex: 21999999999):")
    
    # Se escolheu Salgado, mostra apenas a lista de salgados
    if categoria == "Quero trazer um Salgado":
        if len(salgados_disponiveis) > 0:
            comida_escolhida = st.selectbox("Escolha o seu prato Salgado:", salgados_disponiveis)
        else:
            st.warning("Todos os salgados já foram escolhidos! Por favor, mude lá em cima para a opção de Doces.")
            
    # Se escolheu Doce, mostra apenas a lista de doces
    elif categoria == "Quero trazer um Doce":
        if len(doces_disponiveis) > 0:
            comida_escolhida = st.selectbox("Escolha o seu prato Doce:", doces_disponiveis)
        else:
            st.warning("Todos os doces já foram escolhidos! Por favor, mude lá em cima para a opção de Salgados.")
    
    enviado = st.form_submit_button("Confirmar Prato ✨")

# 6. O que acontece quando clica em confirmar
if enviado:
    if nome and whatsapp and comida_escolhida:
        whatsapp_limpo = "".join(filter(str.isdigit, whatsapp))
        
        nova_linha = pd.DataFrame([{"Nome": nome, "WhatsApp": whatsapp_limpo, "Comida": comida_escolhida}])
        dados_atualizados = pd.concat([dados_existentes, nova_linha], ignore_index=True)
        
        # Salva na planilha
        conn.update(data=dados_atualizados)
        
        # Mensagem do WhatsApp
        tipo_comida = "Salgado" if "Salgado" in categoria else "Doce"
        mensagem = (
            f"Olá! 🎉 Vim confirmar minha presença no *2º Edição Arraiá do Bão*!\n\n"
            f"*Nome:* {nome}\n"
            f"*Meu WhatsApp:* {whatsapp_limpo}\n"
            f"*Categoria:* {tipo_comida}\n"
            f"*Prato escolhido:* {comida_escolhida}\n\n"
            f"Já está salvo no sistema! Nos vemos no dia 18 de Julho! 🌽🔥"
        )
        
        texto_codificado = urllib.parse.quote(mensagem)
        link_whatsapp = f"https://api.whatsapp.com/send?phone=5521999161661&text={texto_codificado}"
        
        st.success(f"Sucesso, {nome}! Seu prato (*{comida_escolhida}*) foi reservado.")
        st.write("📢 **ÚLTIMO PASSO OBRIGATÓRIO:** Clique no botão abaixo para me enviar sua confirmação direto no meu WhatsApp!")
        
        st.link_button("👉 Enviar Confirmação no WhatsApp da Organizadora", link_whatsapp)
        
    elif not comida_escolhida:
        st.error("Não há opções disponíveis na categoria selecionada.")
    else:
        st.error("Por favor, preencha o seu Nome e o seu WhatsApp antes de confirmar!")
