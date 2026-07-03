import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

# 1. Configuração da página
st.set_page_config(page_title="Tutor IA - Situações Problema", layout="centered")
st.title("🤖 Assistente Pedagógico Interativo")
st.write("Espaço de mediação para a resolução de Atividades de Situações Problema.")

# 2. Configuração da API Key (Configurada no Streamlit Cloud)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("Erro ao carregar a chave API. Verifique os 'Secrets' no seu painel.")
    st.stop()

# 3. Base Orientadora (Fundamentada na Teoria Histórico-Cultural)
system_instruction = (
    "Atue como um mediador pedagógico fundamentado na Teoria Histórico-Cultural da Atividade "
    "(perspectivas de Vygotsky, Leontiev, Galperin e Majmutov). Seu objetivo é conduzir estudantes "
    "através de uma Atividade de Situações Problema (ASPD) envolvendo conceitos matemáticos. "
    "Diretrizes Rigorosas:\n"
    "1. NUNCA forneça a resposta final ou o cálculo pronto.\n"
    "2. Ajude o aluno a construir a base orientadora da ação: faça perguntas que o levem a refletir sobre "
    "os conceitos de grandeza, medida, unidade e atributos do objeto.\n"
    "3. Solicite que o estudante explique a lógica de sua tentativa, mediando o avanço do pensamento "
    "empírico para o teórico.\n"
    "4. Se o aluno errar, apresente uma situação ou pergunta reflexiva que evidencie a contradição no raciocínio."
)

# 4. Inicialização do Modelo
if "gemini_sessao" not in st.session_state:
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction,
        generation_config={"temperature": 0.3}
    )
    st.session_state.gemini_sessao = model.start_chat(history=[])

# 5. Histórico
if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []

for msg in st.session_state.historico_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 6. Interação
if entrada := st.chat_input("Digite sua dúvida ou raciocínio..."):
    st.session_state.historico_chat.append({"role": "user", "content": entrada})
    with st.chat_message("user"):
        st.markdown(entrada)

    with st.chat_message("assistant"):
        marcador = st.empty()
        with st.spinner("Analisando..."):
            try:
                resposta = st.session_state.gemini_sessao.send_message(entrada)
                texto = resposta.text
                marcador.markdown(texto)
                st.session_state.historico_chat.append({"role": "assistant", "content": texto})
            except ResourceExhausted:
                marcador.error("Limite de requisições atingido. Aguarde 30 segundos.")
