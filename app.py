import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import urllib.parse

# 1. Configuração visual da página do Arraiá
st.set_page_config(page_title="2º Edição Arraiá do Bão", page_icon="🌽")

st.title("🌽 2º Edição Arraiá do Bão 🔥")
st.write("Escolha o que você vai trazer para a nossa festa no dia 18 de Julho de 2026! Coloque seu nome na opção desejada.")

# 2. SUA LISTA DE COMIDAS (Você pode mudar ou adicionar mais pratos aqui!)
todas_comidas = [
    "Bolo de Fubá", "Canjica", "Pipoca", "Pamonha", "Quentão", 
    "Caldo Verde", "Cachorro Quente", "Salgadinhos", "Doces Juninos", 
    "Milho Cozido", "Bolo de Aipim", "Arroz Doce", "Pastel", "Cuscuz"
]

# 3. Conectando com a sua planilha do Google (usando os Secrets que você configurou)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    dados_existentes = conn.read()
except Exception as e:
    # Se a planilha estiver vazia no primeiro uso, o sistema cria a estrutura básica
    dados_existentes = pd.DataFrame(columns=["Nome", "WhatsApp", "Comida"])

# 4. SISTEMA DE BLOQUEIO: Descobrir o que já foi escolhido na planilha
if not dados_existentes.empty and "Comida" in dados_existentes.columns:
    comidas_ocupadas = dados_existentes["Comida"].dropna().tolist()
else:
    comidas_ocupadas = []

# Filtrar a lista: Só mostra para o convidado o que NÃO está na planilha
comidas_disponiveis = [c for c in todas_comidas if c not in comidas_ocupadas]

# 5. Mostrar o formulário na tela para o convidado preencher
if len(comidas_disponiveis) == 0:
    st.warning("Eita! Todas as comidas da lista já foram escolheram! 🎉")
else:
    # Criamos o formulário
    with st.form("form_arraia", clear_on_submit=True):
        nome = st.text_input("Seu Nome Completo:")
        whatsapp = st.text_input("Seu WhatsApp com DDD (apenas números, ex: 21999999999):")
        comida_escolhida = st.selectbox("Escolha o seu prato:", comidas_disponiveis)
        
        enviado = st.form_submit_button("Confirmar Prato ✨")

    # 6. O que acontece quando o convidado clica no botão de confirmar
    if enviado:
        if nome and whatsapp and comida_escolhida:
            # Remove espaços ou traços que o convidado possa ter digitado no telefone dele
            whatsapp_limpo = "".join(filter(str.isdigit, whatsapp))
            
            # Prepara os dados para salvar na planilha do Google
            nova_linha = pd.DataFrame([{"Nome": nome, "WhatsApp": whatsapp_limpo, "Comida": comida_escolhida}])
            dados_atualizados = pd.concat([dados_existentes, nova_linha], ignore_index=True)
            
            # Salva na planilha de verdade!
            conn.update(data=dados_atualizados)
            
            # --- FUNÇÃO DO WHATSAPP DIRECIONADA PARA VOCÊ ---
            # Escrevemos a mensagem que você vai receber no seu celular
            mensagem = (
                f"Olá! 🎉 Vim confirmar minha presença no *2º Edição Arraiá do Bão*!\n\n"
                f"*Nome:* {nome}\n"
                f"*Meu WhatsApp:* {whatsapp_limpo}\n"
                f"*Prato escolhido:* {comida_escolhida}\n\n"
                f"Já está salvo no sistema! Nos vemos no dia 18 de Julho! 🌽🔥"
            )
            
            # Codifica o texto para formato de link de internet
            texto_codificado = urllib.parse.quote(mensagem)
            
            # Link configurado diretamente com o SEU número de telefone
            link_whatsapp = f"https://api.whatsapp.com/send?phone=5521999161661&text={texto_codificado}"
            
            # Mostra a mensagem de sucesso e o botão verde do WhatsApp na tela
            st.success(f"Sucesso, {nome}! Seu prato (*{comida_escolhida}*) foi reservado.")
            st.write("📢 **ÚLTIMO PASSO OBRIGATÓRIO:** Clique no botão abaixo para me enviar sua confirmação direto no meu WhatsApp!")
            
            # Esse botão abre o SEU WhatsApp com a mensagem pronta na tela do convidado
            st.link_button("
