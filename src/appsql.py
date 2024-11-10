import streamlit as st
import psycopg2
import pandas as pd

# Definição dos parâmetros fixos de conexão
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "testeaabeck"
DB_USER = "abeck"
DB_PASSWORD = "aaBeck"

# Função para conectar ao PostgreSQL
def connect_to_postgres():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        st.success("Conexão bem-sucedida ao banco de dados PostgreSQL!")
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para executar a consulta SQL
def query_database(conn):
    query = st.text_input("Digite sua consulta SQL:")
    if st.button("Executar Consulta"):
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                data = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(data, columns=columns)
                st.dataframe(df)
        except Exception as e:
            st.error(f"Erro ao executar a consulta: {e}")

# Início da aplicação
st.title("Chatbot SQL para PostgreSQL")
conn = connect_to_postgres()
if conn:
    query_database(conn)
    conn.close()