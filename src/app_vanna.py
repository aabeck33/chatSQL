import streamlit as st
import psycopg2
import pandas as pd
from vanna.remote import VannaDefault
import logging
from api_keys import API_KEY_VANNA as API_KEY

# Definição dos parâmetros fixos de conexão
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "testeaabeck"
DB_USER = "abeck"
DB_PASSWORD = "aaBeck"

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

# Inicializa o Vanna
vanna_model_name = "vanna_general"  # ou o nome do modelo apropriado para seu banco: vanna_general / chinook
vn = VannaDefault(model=vanna_model_name, api_key=API_KEY)

# Função para conectar ao banco de dados PostgreSQL
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

# Função para gerar SQL usando Vanna e executar a consulta
def query_database(conn):
    pergunta = st.text_input("O que você gostaria de saber do banco de dados?")
    
    if st.button("Gerar e Executar Consulta"):
        try:
            cur = conn.cursor()
            # Obter as tabelas do banco de dados
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
            tabelas = cur.fetchall()
            # Gerar contexto do esquema
            contexto = "cujas tabelas são:\n"
            for tabela in tabelas:
                contexto += f"- Tabela '{tabela[0]}'\n"


            # Gera o SQL usando a API do Vanna
            prompt = f"Baseado no banco de dados PostgreSQL, {contexto}, escreva uma consulta SQL para a seguinte pergunta:\n\n'{pergunta}'"
            sql = vn.generate_sql(prompt)
            logger.debug("Gerando SQL com Vanna para a pergunta: %s", prompt)
            st.code(sql, language='sql')
            logger.debug("SQL gerado: %s", sql)
            st.write("Consulta gerada:", sql)  # Verifique o output da consulta antes de executar
            
            # Executa a consulta no banco de dados PostgreSQL
            with conn.cursor() as cur:
                cur.execute(sql)
                data = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(data, columns=columns)
                st.dataframe(df)
        except Exception as e:
            st.error(f"Erro ao executar a consulta: {e}")
            logger.error("Erro ao executar a consulta: %s", e)

# Início da aplicação
st.title("Chatbot SQL para PostgreSQL usando Vanna")
conn = connect_to_postgres()
if conn:
    query_database(conn)
    conn.close()
