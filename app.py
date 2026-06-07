import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# 1. Configuração visual da página do Arraiá
st.set_page_config(page_title="2º Edição Arraiá do Bão", page_icon="🌽")

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
    "Maçã do amor", "Algodão doce", "Arroz doce","Paçoca","Palha Italiana"
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

# 5. Escolha da categoria FORA do formulário para atualizar instantaneamente
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
            comida_final = escolha_lista
            
    elif categoria == "Quero trazer um Doce":
        escolha_lista = st.selectbox("Escolha o seu prato Doce:", doces_disponiveis)
        if escolha_lista == "Outros":
            outro_prato = st.text_input("Escreva aqui qual DOCE diferente você vai trazer (Obrigatório):")
            comida_final = outro_prato
        else:
            comida_final = escolha_lista
    
    enviado = st.form_submit_button("Confirmar Prato ✨")

# 6. O que acontece quando clica em confirmar
if enviado:
    if nome and whatsapp and comida_final and comida_final.strip():
        whatsapp_limpo = "".join(filter(str.isdigit, whatsapp))
        comida_salvar = comida_final.strip()
        
        nova_linha = pd.DataFrame([{"Nome": nome, "WhatsApp": whatsapp_limpo, "Comida": comida_salvar}])
        dados_atualizados = pd.concat([dados_existentes, nova_linha], ignore_index=True)
        
        # Salva na planilha imediatamente
        conn.update(data=dados_atualizados)
        
        # Guardamos os dados de sucesso na memória temporária do Streamlit
        st.session_state["sucesso_nome"] = nome
        st.session_state["sucesso_comida"] = comida_salvar
        st.session_state["sucesso_whatsapp"] = whatsapp_limpo
        st.session_state["sucesso_categoria"] = "Salgado" if "Salgado" in categoria else "Doce"
        
        st.rerun()
        
    else:
        st.error("Por favor, preencha todos os campos! Se você selecionou 'Outros', é obrigatório escrever o nome do prato.")

# 7. Exibe a tela de sucesso e o botão do WhatsApp (Montado de forma segura contra erros de aspas)
if "sucesso_nome" in st.session_state:
    s_nome = st.session_state["sucesso_nome"]
    s_comida = st.session_state["sucesso_comida"]
    s_whatsapp = st.session_state["sucesso_whatsapp"]
    s_cat = st.session_state["sucesso_categoria"]
    
    # Texto estruturado de forma linear e segura
    mensagem = f"Olá! 🎉 Vim confirmar minha presença no *2º Edição Arraiá do Bão*!\n\n*Nome:* {s_nome}\n*Meu WhatsApp:* {s_whatsapp}\n*Categoria:* {s_cat}\n*Prato escolhido:* {s_comida}\n\nJá está salvo no sistema! Nos vemos no dia 18 de Julho! 🌽🔥"
    
    texto_codificado = urllib.parse.quote(mensagem)
    link_whatsapp = f"https://api.whatsapp.com/send?phone=5521999161661&text={texto_codificado}"
    
    st.success(f"Sucesso, {s_nome}! Seu prato (*{s_comida}*) foi reservado e já sumiu do menu para os próximos convidados!")
    st.write("📢 **ÚLTIMO PASSO OBRIGATÓRIO:** Clique no botão abaixo para me enviar sua confirmação direto no meu WhatsApp!")
    st.link_button("👉 Enviar Confirmação no WhatsApp da Organizadora", link_whatsapp)
    
    del st.session_state["sucesso_nome"]

# 8. MURAL PÚBLICO: QUADRO DE COMIDAS JÁ ESCOLHIDAS
st.write("---")
st.subheader("📋 Quem já confirmou e o que vai trazer:")

if not dados_existentes.empty:
    mural_dados = dados_existentes.copy()
    if "Nome" in mural_dados.columns and "Comida" in mural_dados.columns:
        tabela_publica = mural_dados[["Nome", "Comida"]].copy()
        tabela_publica.columns = ["Convidado(a)", "Prato Confirmado 🍽️"]
        st.dataframe(tabela_publica, use_container_width=True, hide_index=True)
else:
    st.info("Ainda não temos pratos confirmados. Seja o primeiro! 🥳")
