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
    "Torta de frango", "Torta de sardinha", "Empadão de frango", "Pipoca Salgada"
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
    dados_existentes = pd.DataFrame(columns=["Nome", "WhatsApp", "Comida", "Comprovante"])

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
            comida_final = escolha_lista
            
    elif categoria == "Quero trazer um Doce":
        escolha_lista = st.selectbox("Escolha o seu prato Doce:", doces_disponiveis)
        if escolha_lista == "Outros":
            outro_prato = st.text_input("Escreva aqui qual DOCE diferente você vai trazer (Obrigatório):")
            comida_final = outro_prato
        else:
            comida_final = escolha_lista
            
    # Upload do Comprovante (Obrigatório para validação no site)
    comprovante_arquivo = st.file_uploader("Anexe seu comprovante aqui no site (Obrigatório):", type=["png", "jpg", "jpeg"])
    
    enviado = st.form_submit_button("Confirmar Prato ✨")

# 6. O que acontece quando clica em confirmar
if enviado:
    if nome and whatsapp and comida_final and comida_final.strip() and comprovante_arquivo is not None:
        whatsapp_limpo = "".join(filter(str.isdigit, whatsapp))
        comida_salvar = comida_final.strip()
        
        # Salva o registro de que o arquivo foi enviado na planilha
        texto_comprovante = f"Enviado no Site ({comprovante_arquivo.name})"
        
        nova_linha = pd.DataFrame([{
            "Nome": nome, 
            "WhatsApp": whatsapp_limpo, 
            "Comida": comida_salvar,
            "Comprovante": texto_comprovante
        }])
        dados_atualizados = pd.concat([dados_existentes, nova_linha], ignore_index=True)
        conn.update(data=dados_atualizados)
        
        # Guardamos os dados de sucesso na memória temporária
        st.session_state["sucesso_nome"] = nome
        st.session_state["sucesso_comida"] = comida_salvar
        st.session_state["sucesso_whatsapp"] = whatsapp_limpo
        st.session_state["sucesso_categoria"] = "Salgado" if "Salgado" in categoria else "Doce"
        
        st.rerun()
        
    else:
        st.error("Por favor, preencha todos os campos e anexe o seu Comprovante! Ele é obrigatório.")

# 7. Exibe a tela de sucesso e ensina a mandar a foto no WhatsApp
if "sucesso_nome" in st.session_state:
    s_nome = st.session_state["sucesso_nome"]
    s_comida = st.session_state["sucesso_comida"]
    s_whatsapp = st.session_state["sucesso_whatsapp"]
    s_cat = st.session_state["sucesso_categoria"]
    
    mensagem = (
        f"Olá! 🎉 Vim confirmar minha presença no *2º Edição Arraiá do Bão*!\n\n"
        f"*Nome:* {s_nome}\n"
        f"*Meu WhatsApp:* {s_whatsapp}\n"
        f"*Categoria:* {s_cat}\n"
        f"*Prato escolhido:* {s_comida}\n\n"
        f" Estou enviando a foto do meu comprovante em anexo aqui nesta conversa! 🌽🔥"
    )
    
    texto_codificado = urllib.parse.quote(mensagem)
    link_whatsapp = f"https://api.whatsapp.com/send?phone=5521999161661&text={texto_codificado}"
    
    st.success(f"Sucesso, {s_nome}! Seus dados foram salvos e o prato (*{s_comida}*) foi reservado.")
    
    # Adicionamos instruções bem visíveis de como você vai receber a imagem
    st.info("📸 **COMO ENVIAR O COMPROVANTE PARA A ORGANIZADORA:**\n\n"
            "1. Clique no botão verde abaixo para abrir o WhatsApp.\n"
            "2. Envie o texto de confirmação que já vai aparecer digitado.\n"
            "3. **Anexe a foto do seu comprovante nesta mesma conversa** para que eu possa validar! 😉")
            
    st.link_button("👉 Abrir WhatsApp para Enviar Texto e Comprovante", link_whatsapp)
    
    del st.session_state["sucesso_nome"]
