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
    "Maçã do amor", "Algodão doce", "Arroz doce", "Palha Italiana"
]

# 3. Conectando com a sua planilha do Google (Zerar o cache com ttl=0)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    dados_existentes = conn.read(ttl=0)
except Exception as e:
    dados_existentes = pd.DataFrame(columns=["Nome", "WhatsApp", "Comida"])

# 4. SISTEMA DE BLOQUEIO INDEPENDENTE (Ignora a palavra Outros na hora de bloquear)
if not dados_existentes.empty and "Comida" in dados_existentes.columns:
    comidas_ocupadas = [
        c.strip() for c in dados_existentes["Comida"].dropna().astype(str) 
        if c.strip().lower() not in ["outros salgados", "outros doces"]
    ]
else:
    comidas_ocupadas = []

# Criamos as listas já filtradas
salgados_filtrados = [f"Salgado: {c}" for c in comidas_salgadas if c.strip() not in comidas_ocupadas]
doces_filtrados = [f"Doce: {c}" for c in comidas_doces if c.strip() not in comidas_ocupadas]

# Juntamos tudo em uma lista única
lista_completa_pratos = salgados_filtrados + ["Outros Salgados"] + doces_filtrados + ["Outros Doces"]

# 5. Criamos o formulário COMPLETO
with st.form("form_arraia", clear_on_submit=True):
    nome = st.text_input("Seu Nome Completo:")
    whatsapp = st.text_input("Seu WhatsApp com DDD (apenas números, ex: 21999999999):")
    
    # Seleção do prato unificada
    escolha_prato = st.selectbox("Escolha o que você vai trazer (Salgados ou Doces):", lista_completa_pratos)
    
    # Campo de texto livre para especificar pratos novos
    especificar_outros = st.text_input("Se escolheu 'Outros Salgados' ou 'Outros Doces', escreva o nome do prato aqui:")
    
    enviado = st.form_submit_button("Confirmar Prato ✨")

# 6. O que acontece quando clica em confirmar
if enviado:
    if nome and whatsapp:
        comida_final = ""
        
        if "Outros" in escolha_prato:
            if especificar_outros.strip() and especificar_outros.strip().lower() not in ["outros", "outros salgados", "outros doces"]:
                comida_final = especificar_outros.strip()
                categoria_sucesso = "Salgado" if "Salgados" in escolha_prato else "Doce"
            else:
                st.error("Por favor, especifique o nome real do prato no campo de texto livre!")
                st.stop()
        else:
            comida_final = escolha_prato.split(": ")[1]
            categoria_sucesso = "Salgado" if "Salgado:" in escolha_prato else "Doce"

        if comida_final:
            whatsapp_limpo = "".join(filter(str.isdigit, whatsapp))
            nova_linha = pd.DataFrame([{"Nome": nome, "WhatsApp": whatsapp_limpo, "Comida": comida_final}])
            dados_atualizados = pd.concat([dados_existentes, nova_linha], ignore_index=True)
            
            conn.update(data=dados_atualizados)
            
            st.session_state["sucesso_nome"] = nome
            st.session_state["sucesso_comida"] = comida_final
            st.session_state["sucesso_whatsapp"] = whatsapp_limpo
            st.session_state["sucesso_categoria"] = categoria_sucesso
            
            st.rerun()
    else:
        st.error("Por favor, preencha o seu Nome e o seu WhatsApp!")

# 7. Exibe a tela de sucesso e o botão do WhatsApp
if "sucesso_nome" in st.session_state:
    s_nome = st.session_state["sucesso_nome"]
    s_comida = st.session_state["sucesso_comida"]
    s_whatsapp = st.session_state["sucesso_whatsapp"]
    s_cat = st.session_state["sucesso_categoria"]
    
    mensagem = f"Olá! 🎉 Vim confirmar minha presença no *2º Edição Arraiá do Bão*!\n\n*Nome:* {s_nome}\n*Meu WhatsApp:* {s_whatsapp}\n*Categoria:* {s_cat}\n*Prato escolhido:* {s_comida}\n\nJá está salvo no sistema! Nos vemos no dia 18 de Julho! 🌽🔥"
    texto_codificado = urllib.parse.quote(mensagem)
    link_whatsapp = f"https://api.whatsapp.com/send?phone=5521999161661&text={texto_codificado}"
    
    st.success(f"Sucesso, {s_nome}! Seu prato (*{s_comida}*) foi reservado com sucesso!")
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

# 🌟 TRUQUE DE ESPAÇO: Criando um espaço invisível no fundo da página
# Isso garante espaço físico embaixo do formulário para o menu abrir para baixo!
st.write("\n" * 15)
