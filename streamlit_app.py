# streamlit_app.py
import streamlit as st
import requests

# URL de tu API de FastAPI
API_URL = "http://localhost:8000/human_query"

def main():
    st.title("Chatbot para Consultas de la Base de Datos")
    
    # Campo de entrada para la consulta del usuario
    user_query = st.text_input("Introduce tu consulta:")
    
    if st.button("Enviar"):
        if user_query:
            try:
                response = requests.post("http://localhost:8000/human_query", json={"human_query": user_query})
                response.raise_for_status()  # Lanza un error si la respuesta HTTP tiene un código de error
                result = response.json().get("result")
                st.write("Respuesta del chatbot:")
                st.write(result)
            except requests.exceptions.HTTPError as http_err:
                st.error(f"Error HTTP: {http_err}")
            except requests.exceptions.RequestException as req_err:
                st.error(f"Error en la solicitud: {req_err}")
            except Exception as e:
                st.error(f"Error inesperado: {e}")
        else:
            st.warning("Por favor, introduce una consulta")

if __name__ == "__main__":
    main()
