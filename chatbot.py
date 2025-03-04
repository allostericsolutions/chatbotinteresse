import streamlit as st
import openai

# Configuración de la API Key (desde Streamlit Secrets)
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("Error: No se encontró la clave 'OPENAI_API_KEY' en los secretos de Streamlit. Asegúrate de haberla configurado correctamente.")
    st.stop()
except Exception as e:
    st.error(f"Error al acceder a los secretos de Streamlit: {e}")
    st.stop()


# Función para cargar el prompt inicial desde el archivo
def load_initial_prompt(filepath):
    try:
        with open(filepath, "r") as f:
            return f.read()
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo de prompt inicial en '{filepath}'.")
        st.stop()
    except Exception as e:
        st.error(f"Error al leer el archivo de prompt inicial: {e}")
        st.stop()


# Función para obtener la respuesta del modelo (Completion API)
def get_completion(prompt, model="gpt-4o-mini", max_tokens=12000):  # Modelo y max_tokens como parámetros
    try:
        messages = [{"role": "user", "content": prompt}]
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
            max_tokens=max_tokens, 12000# Especifica la longitud máxima de la respuesta
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error al obtener la respuesta del modelo: {e}")
        return "Lo siento, hubo un problema al obtener la respuesta del modelo."


# Cargar el prompt inicial y almacenarlo en st.session_state
if "initial_prompt" not in st.session_state:
    st.session_state.initial_prompt = load_initial_prompt("prompts/initial_prompt.txt")

# Mensaje de bienvenida
welcome_message = "Hola, ¿cómo puedo ayudarte?"

# Inicializar el historial del chat en la sesión (si no existe)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": welcome_message}]

# Interfaz de Streamlit
st.title("Asistente Virtual Interesse")

# Mostrar los mensajes del chat existentes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar la entrada del usuario
if prompt := st.chat_input("Escribe tu mensaje aquí..."):
    # Añadir el mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Construir el prompt completo para el modelo
    full_prompt = f"{st.session_state.initial_prompt}\nUsuario: {prompt}\nChatbot:"

    # Obtener la respuesta del modelo
    with st.spinner("Esperando respuesta del modelo..."):
        response = get_completion(full_prompt)

    # Añadir la respuesta del modelo al historial
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
