import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Tutor IA - Situações Problema", layout="centered")
st.title("🤖 Assistente Pedagógico Interativo")

# 1. Configuração da API
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("Erro ao carregar a chave API. Verifique as configurações de 'Secrets'.")
    st.stop()

# 2. Definição da instrução do sistema
system_instruction = """
Atue como um mediador pedagógico fundamentado na Teoria Histórico-Cultural da Atividade.
Seu objetivo é conduzir estudantes através de uma Atividade de Situações Problema Discente (ASPD).
Diretrizes:
1. NUNCA forneça a resposta final ou o cálculo pronto de imediato.
2. Ajude o aluno a construir a base orientadora da ação.
3. Solicite que o estudante verbalize a lógica de sua tentativa.
4. Se o aluno errar, apresente uma nova pergunta reflexiva que evidencie a contradição no raciocínio.
"""

# 3. Inicialização do modelo e chat
if "gemini_model" not in st.session_state:
    st.session_state.gemini_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction,
        generation_config={"temperature": 0.3}
    )
if "gemini_sessao" not in st.session_state:
    st.session_state.gemini_sessao = st.session_state.gemini_model.start_chat(history=[])

# 4. Interface do Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Digite aqui a sua dúvida ou raciocínio..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.gemini_sessao.send_message(prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Erro ao processar mensagem: {e}")
