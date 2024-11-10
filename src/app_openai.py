import openai
import streamlit as st
import pandas as pd
import psycopg2
from streamlit_option_menu import option_menu
import logging


# Parâmetros de conexão (fixos no código)
server_host = "localhost"
server_port = 5432
database_name = "testeaabeck"
DB_username = "abeck"
password = "aaBeck"
# Configuração da chave de API OpenAI
openai.api_key = "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"
#FUnção que gera o SQL com a openAI
def gerar_sql(question, schema_info=""):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em SQL. Converta perguntas em consultas SQL."},
                {"role": "user", "content": f"Esquema do Banco de Dados:\n{schema_info}\n\nPergunta: {question}\n\nSQL:"}
                ],
            temperature=0.2
        )
        response_string = str(response.choices[0].message.content)
        sql_query = response_string[7:response_string.index(';')]
        return sql_query
    except Exception as e:
        logging.error(f"Erro ao gerar SQL: {e}")
        return None

def gerar_sql4(question, schema_info=""):
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em SQL. Converta perguntas em consultas SQL."},
                {"role": "user", "content": f"Esquema do Banco de Dados:\n{schema_info}\n\nPergunta: {question}\n\nSQL:"}
                ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Erro ao gerar SQL: {e}")
        return None

# Função para executar a consulta no banco de dados
def executar_sql(sql, con):
    try:
        return pd.read_sql(sql, con)
    except Exception as e:
        logging.error(f"Erro ao executar a consulta: {e}")
        return None

# Conexão com o PostgreSQL
def conectar_postgres():
    try:
        conn = psycopg2.connect(
            host=server_host,
            port=server_port,
            dbname=database_name,
            user=DB_username,
            password=password
        )
        return conn
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função principal para consultar o banco de dados
def query_database():
    query = st.text_input("O que você gostaria de saber do banco de dados?", key="query")
    
    if query:
        prompt = f"Crie uma consulta SQL para: {query}"
        
        # Conectar ao banco e executar a consulta
        conn = conectar_postgres()
        if conn:
            schema_info = get_database_schema(conn)
            sql_gerado = gerar_sql4(prompt, schema_info)
            st.write(f"SQL gerado: {sql_gerado}")
            df = executar_sql(sql_gerado, conn)
            if df is not None:
                st.dataframe(df)
            else:
                st.error("Erro ao executar a consulta SQL.")
            conn.close()
        else:
            st.error("Falha na conexão com o banco de dados.")

def get_database_schema(con):
    contexto = ""
    cur = con.cursor()
    # Obter as tabelas do banco de dados
    cur.execute('''SELECT tables.table_name, columns.column_name, pkey.column_name as primkey
                    FROM information_schema.tables tables
                    inner join information_schema.columns columns on columns.table_name = tables.table_name
                    left join information_schema.table_constraints tables_const on tables_const.table_name = tables.table_name
                    and tables_const.constraint_type in ('PRIMARY KEY', 'FOREIGN KEY')
                    JOIN information_schema.key_column_usage pkey on pkey.constraint_name = tables_const.constraint_name
                    AND pkey.table_name = tables_const.table_name AND pkey.table_schema = tables_const.table_schema
                    WHERE tables.table_schema='public';'''
                )
    tabelas = cur.fetchall()
    # Gerar contexto do esquema
    for tabela in tabelas:
        contexto += f"- Tabela '{tabela[0]}'\n"
    return contexto


# Interface do Streamlit
st.title("Chatbot SQL com OpenAI")

# Seleção do banco de dados
with st.sidebar:
    selected = option_menu(
        menu_title="Conectar ao Banco de Dados",
        options=["PostgreSQL"]
    )

if selected == "PostgreSQL":
    st.subheader('Conectando ao banco de dados PostgreSQL')
    query_database()


# https://rubsphp.blogspot.com/2011/04/tabelas-e-colunas-no-postgresql.html
