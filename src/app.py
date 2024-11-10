import streamlit as st
import requests
import pandas as pd
import psycopg2

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

# Função para gerar SQL com a API da Hugging Face
def gerar_sql_com_huggingface(pergunta, api_key):
    url = "https://api-inference.huggingface.co/models/suriya7/t5-base-text-to-sql"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": pergunta}

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        output = response.json()
        return output[0]['generated_text'] if output else None
    else:
        st.error(f"Erro ao gerar SQL: {response.status_code}")
        return None

# Função para executar o SQL no banco de dados
def executar_sql_no_postgres(sql, conn):
    try:
        return pd.read_sql(sql, conn)
    except Exception as e:
        st.error(f"Erro ao executar a consulta SQL: {e}")
        return None

# Configuração da chave de API da Hugging Face
API_KEY = "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"  # Substitua pelo seu token da API Hugging Face

# Configuração da interface do Streamlit
st.title("Consultas SQL usando Linguagem Natural com Hugging Face")
pergunta = st.text_input("Faça sua pergunta sobre o banco de dados:")
consultar = st.button("Consultar")

# Lógica para processar a consulta quando o botão for clicado
if consultar and pergunta:
    # Gerar a consulta SQL
    st.write("Gerando consulta SQL...")
    sql_gerado = gerar_sql_com_huggingface(pergunta, API_KEY)

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
