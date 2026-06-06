import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# 1. Configuração visual da página do Arraiá
st.set_page_config(page_title="2º Edição Arraiá do Bão", page_icon="🌽")

st.title("🌽 2º Edição Arraiá do Bão 🔥")
st.write("Escolha o que você vai trazer para a nossa festa no dia 18 de Julho de 2026! Coloque seu nome na opção desejada.")

# 2. SEU CARDÁPIO DIVIDIDO
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

# Junta tudo para o sistema saber o total de pratos
todas_comidas = comidas_salgadas + comidas_doces

# 3. Conectando com a sua planilha do Google
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    dados_existentes = conn.read()
except Exception as e:
    dados_existentes = pd.DataFrame(columns=["Nome", "WhatsApp", "Comida"])

# 4. SISTEMA DE BLOQUEIO: Descobrir o que já foi escolhido
if not dados_existentes.empty and "Comida" in dados_existentes.columns:
    comidas_ocupadas = dados_existentes["Comida"].dropna().tolist()
else:
    comidas_ocupadas = []

# Filtrar as listas: Remove o que já foi escolhido por outras pessoas
salgados_disponiveis = [c for c in comidas_salgadas if c not in comidas_ocupadas]
doces_disponiveis = [c for c in comidas_doces if c not in comidas_ocupadas]
total_disponivel = [c for c in todas_comidas if c not in comidas_ocupadas]

# 5. Mostrar o formulário na tela
if len(total_disponivel) == 0:
    st.warning("Eita! Todas as comidas da lista já foram escolhidas! 🎉")
else:
    with st.form("form_arraia", clear_on_submit=True):
        nome = st.text_input("Seu Nome Completo:")
        whatsapp = st.text_input("Seu WhatsApp com DDD (apenas números, ex: 21999999999):")
        
        # Primeiro Dropdown: Escolher a categoria
        categoria = st.selectbox("O que você quer trazer?", ["Salgados", "Doces"])
        
        # Segundo Dropdown: Mostra as opções baseado na categoria escolhida
        if categoria == "Salgados":
            if len(salgados_disponiveis) > 0:
                comida_escolhida = st.selectbox("Escolha o seu prato Salgado:", salgados_disponiveis)
            else:
                st.warning("Todos os salgados já foram escolhidos! Escolha a categoria Doces.")
                comida_escolhida = None
        else:
            if len(doces_disponiveis) > 0:
                comida_escolhida = st.selectbox("Escolha o seu prato Doce:", doces_disponiveis)
            else:
                st.warning("Todos os doces já foram escolhidos! Escolha a categoria Salgados.")
                comida_escolhida = None
        
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
            mensagem = (
                f"Olá! 🎉 Vim confirmar minha presença no *2º Edição Arraiá do Bão*!\n\n"
                f"*Nome:* {nome}\n"
                f"*Meu WhatsApp:* {whatsapp_limpo}\n"
                f"*Tipo:* {categoria}\n"
                f"*Prato escolhido:* {comida_escolhida}\n\n"
                f"Já está salvo no sistema! Nos vemos no dia 18 de Julho! 🌽🔥"
            )
            
            texto_codificado = urllib.parse.quote(mensagem)
            link_whatsapp = f"https://api.whatsapp.com/send?phone=5521999161661&text={texto_codificado}"
            
            st.success(f"Sucesso, {nome}! Seu prato (*{comida_escolhida}*) foi reservado.")
            st.write("📢 **ÚLTIMO PASSO OBRIGATÓRIO:** Clique no botão abaixo para me enviar sua confirmação direto no meu WhatsApp!")
            
            st.link_button("👉 Enviar Confirmação no WhatsApp da Organizadora", link_whatsapp)
            
        elif not comida_escolhida:
            st.error("Não há opções disponíveis nesta categoria. Mude para a outra categoria!")
        else:
            st.error("Por favor, preencha o seu Nome e o seu WhatsApp antes de confirmar!")
