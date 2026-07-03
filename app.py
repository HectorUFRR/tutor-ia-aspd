import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. Configuração visual da página web do Streamlit
st.set_page_config(page_title="Tutor IA - Situações Problema", layout="centered")

st.title("🤖 Assistente Pedagógico Interativo")
st.write("Espaço de mediação para a resolução de Atividades de Situações Problema.")

# 2. Configuração de Segurança da API Key via Secrets
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error("Erro ao carregar a chave API. Verifique as configurações de 'Secrets'.")
    st.stop()

# 3. Base Orientadora fundamentada na Teoria Histórico-Cultural
system_instruction = (
    "Atue como um mediador pedagógico fundamentado na Teoria Histórico-Cultural da Atividade "
    "(perspectivas de Vygotsky, Leontiev, Galperin e Majmutov). Seu objetivo é conduzir estudantes "
    "através de uma Atividade de Situações Problema envolvendo conceitos matemáticos (como multiplicação e divisão). "
    "Diretrizes Rigorosas:\n"
    "1. NUNCA fornece a resposta final ou o cálculo pronto de imediato.\n"
    "2. Ajude o aluno a construir a base orientadora da ação: quando ele apresentar uma dúvida ou cometer um erro, "
    "faça perguntas que o levem a refletir sobre as propriedades da operação.\n"
    "3. Solicite que o estudante verbalize e explique a lógica de sua tentativa, mediando o avanço do pensamento empírico para o teórico.\n"
    "4. Se o aluno errar, apresente uma nova situação ou uma pergunta reflexiva que evidencie a contradição no raciocínio dele."
)

# 4. Inicialização do Modelo e Gerenciamento da Sessão de Chat
if "historico_chat" not in st.session_state:
    st.session_state.historico_chat = []
    st.session_state.gemini_sessao = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3
        )
    )

# 5. Exibe as mensagens anteriores na tela
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
            try:
                # Tenta enviar a mensagem para a API do Gemini
                resposta_modelo = st.session_state.gemini_sessao.send_message(entrada_estudante)
                texto_mediacao = resposta_modelo.text
                marcador_resposta.markdown(texto_mediacao)
                
                # Só adiciona no histórico se o envio ocorreu com sucesso
                st.session_state.historico_chat.append({"role": "assistant", "content": texto_mediacao})
            
            except APIError as e:
                # Captura erros de limite de cota de forma amigável
                if e.code == 429:
                    texto_erro = (
                        "⚠️ **Muitos acessos simultâneos!** O limite de requisições "
                        "por minuto foi atingido. Por favor, aguarde cerca de 30 a 40 segundos e envie sua mensagem novamente."
                    )
                else:
                    texto_erro = f"⚠️ Erro na API do Gemini: {e.message}"
                marcador_resposta.error(texto_erro)
