import streamlit as st
import google.generativeai as genai

# 1. Configuração visual da página web do Streamlit
st.set_page_config(page_title="Tutor IA - Situações Problema", layout="centered")

st.title("🤖 Assistente Pedagógico Interativo")
st.write("Espaço de mediação para a resolução de Atividades de Situações Problema.")

# 2. Configuração de Segurança da API Key
# Substitua pelo código gerado no Google AI Studio (a sua chave que termina em ...drdQ)
API_KEY = st.secrets["GEMINI_API_KEY"]
 
if not API_KEY or API_KEY == "SUA_API_KEY_AQUI":
    st.error("Por favor, configure a sua API Key do Google AI Studio no código para iniciar.")
else:
    genai.configure(api_key=API_KEY)

    # 3. Base Orientadora fundamentada na Teoria Histórico-Cultural
    system_instruction = (
        "Atue como um mediador pedagógico fundamentado na Teoria Histórico-Cultural da Atividade "
        "(perspectivas de Vygotsky, Leontiev, Galperin e Majmutov). Seu objetivo é conduzir estudantes "
        "através de uma Atividade de Situações Problema envolvendo conceitos matemáticos (como multiplicação e divisão). "
        "Diretrizes Rigorosas:\n"
        "1. NUNCA forneça a resposta final ou o cálculo pronto de imediato.\n"
        "2. Ajude o aluno a construir a base orientadora da ação: quando ele apresentar uma dúvida ou cometer um erro, "
        "faça perguntas que o levem a refletir sobre as propriedades da operação.\n"
        "3. Solicite que o estudante verbalize e explique a lógica de sua tentativa, mediando o avanço do pensamento empírico para o teórico.\n"
        "4. Se o aluno errar, apresente uma nova situação ou uma pergunta reflexiva que evidencie a contradição no raciocínio dele."
    )

    # 4. Inicialização do Modelo com os parâmetros do Playground
    @st.cache_resource
    def inicializar_modelo():
        return genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction,
            generation_config={"temperature": 0.3}
        )
# Inicializar o modelo e o chat
model = inicializar_modelo()

if "gemini_sessao" not in st.session_state:
    st.session_state.gemini_sessao = model.start_chat(history=[])

# Interface do chat
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
        response = st.session_state.gemini_sessao.send_message(prompt)
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    # 5. Gerenciamento do Histórico de Conversa na Memória da Página
    if "historico_chat" not in st.session_state:
        st.session_state.historico_chat = []
        st.session_state.gemini_sessao = model.start_chat(history=[])

    # Exibe as mensagens anteriores na tela
    for mensagem in st.session_state.historico_chat:
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])

    # 6. Campo de Entrada para o Estudante interagir
    if entrada_estudante := st.chat_input("Digite aqui a sua dúvida ou raciocínio..."):
        
        with st.chat_message("user"):
            st.markdown(entrada_estudante)
        st.session_state.historico_chat.append({"role": "user", "content": entrada_estudante})

        with st.chat_message("assistant"):
            marcador_resposta = st.empty()
            with st.spinner("A analisar o raciocínio..."):
                resposta_modelo = st.session_state.gemini_sessao.send_message(entrada_estudante)
                texto_mediacao = resposta_modelo.text
                marcador_resposta.markdown(texto_mediacao)
        
        st.session_state.historico_chat.append({"role": "assistant", "content": texto_mediacao})
