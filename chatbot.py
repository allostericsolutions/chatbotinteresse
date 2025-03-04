import streamlit as st
import openai

# ID del asistente
assistant_id = "asst_XNzi1UgDLnL92R4li9jEXiJ0"

# Configuración de la API Key (desde Streamlit Secrets)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("Error: No se encontró la clave 'OPENAI_API_KEY' en los secretos de Streamlit. Asegúrate de haberla configurado correctamente.")
    st.stop()
except Exception as e:
    st.error(f"Error al acceder a los secretos de Streamlit: {e}")
    st.stop()

# Inicializar el hilo (thread) si no existe en la sesión
if "thread_id" not in st.session_state:
    try:
        thread = openai.beta.threads.create()
        st.session_state.thread_id = thread.id
    except Exception as e:
        st.error(f"Error al crear el hilo: {e}")
        st.stop()


# Función para enviar mensajes al asistente y obtener la respuesta
def run_assistant(thread_id, user_message):
    try:
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )

        # Esperar a que termine la ejecución
        while run.status != "completed":
            run = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        # Obtener los mensajes del hilo
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[0].text.value
        return response
    except Exception as e:
        st.error(f"Error al interactuar con el asistente: {e}")
        return "Lo siento, hubo un problema al obtener la respuesta del asistente."


# Interfaz de Streamlit
st.title("Chatbot con Asistente de OpenAI")

# Inicializar el historial del chat en la sesión (si no existe)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar los mensajes del chat existentes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar la entrada del usuario
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # Añadir el mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Mostrar el mensaje del usuario inmediatamente
    with st.chat_message("user"):
        st.markdown(prompt)

    # Obtener la respuesta del asistente
    with st.spinner("Esperando respuesta del asistente..."):
        assistant_response = run_assistant(st.session_state.thread_id, prompt)

    # Añadir la respuesta del asistente al historial
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    # Mostrar la respuesta del asistente inmediatamente
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
