import streamlit as st
import requests
import pandas as pd
import psycopg2
from api_keys import API_KEY_DEEPAI as API_KEY

# Configurações para conexão com o banco de dados PostgreSQL
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "testeaabeck"
DB_USER = "abeck"
DB_PASSWORD = "aaBeck"

# Função para conectar ao PostgreSQL
def conectar_postgres():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para gerar SQL com a API do DeepAI
def gerar_sql_como_deepai(pergunta, api_key):
    url = "https://api.deepai.org/api/text2sql"
    headers = {'api-key': api_key}
    try:
        response = requests.post(url, headers=headers, data={'text': pergunta})
        if response.status_code == 200:
            return response.json().get('output')
        elif response.status_code == 500:
            st.error("Erro 500: Problema no servidor do DeepAI. Tente novamente mais tarde.")
            return None
        else:
            st.error(f"Erro ao gerar SQL: Código de status {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Ocorreu um erro ao acessar a API: {e}")
        return None


# Função para executar o SQL no banco de dados
def executar_sql_no_postgres(sql, conn):
    try:
        return pd.read_sql(sql, conn)
    except Exception as e:
        st.error(f"Erro ao executar a consulta SQL: {e}")
        return None

# Configuração da interface do Streamlit
st.title("Consultas SQL usando Linguagem Natural")
pergunta = st.text_input("Faça sua pergunta sobre o banco de dados:")
consultar = st.button("Consultar")

# Lógica para processar a consulta quando o botão for clicado
if consultar and pergunta:
    # Gerar a consulta SQL
    st.write("Gerando consulta SQL...")
    sql_gerado = gerar_sql_como_deepai(pergunta, API_KEY)

    if sql_gerado:
        st.write(f"Consulta SQL gerada: `{sql_gerado}`")
        
        # Conectar ao banco e executar a consulta
        conn = conectar_postgres()
        if conn:
            st.write("Executando consulta no banco de dados...")
            resultado = executar_sql_no_postgres(sql_gerado, conn)
            if resultado is not None:
                st.write("Resultados:")
                st.dataframe(resultado)
            conn.close()
