


import MySQLdb
import pyodbc
from turtle import pd
import pyodbc
import base64
import qrcode
from io import BytesIO



def dados_qualidade(ref):
    


    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    query = f"""
            select st.ref,design,st.inactivo,st.u_tipoart,st.u_tamanho,st.u_nave,st.unidade,usr1,usr2,lang4,lang5,st.familia,st.fornecedor,cancpos,peso,st.stock,st.obs,sa.armazem,sa.stock as stock_arm from st 
            inner join sa on sa.ref=st.ref
            where st.ref='{ref}' and sa.stock>0 and st.stns = 0

                """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    print(query)
    dados = []
    for row in rows:
        dado = {
            'ref': row.ref,
            'design': row.design,
            'inactivo': row.inactivo,
            'u_tipoart': row.u_tipoart,
            'u_tamanho': row.u_tamanho,
            'u_nave': row.u_nave,
            'unidade': row.unidade,
            'usr1': row.usr1,
            'usr2': row.usr2,
            'lang4': row.lang4,
            'lang5': row.lang5,
            'familia': row.familia,
            'fornecedor': row.fornecedor,
            'cancpos': row.cancpos,
            'peso': row.peso,
            'stock': row.stock,
            'obs': row.obs,
            'armazem': row.armazem,
            'stock_arm': row.stock_arm
        }

        dados.append(dado)
    return dados

def atualizar_cancpos(ref, cancpos):
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
        cursor = conn.cursor()
        query = f"UPDATE st SET cancpos = ? WHERE ref = ?"
        cursor.execute(query, (cancpos, ref))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao atualizar cancpos: {e}")
        return False
    
def atualizar_peso(ref, peso):
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
        cursor = conn.cursor()
        query = f"UPDATE st SET peso = ? WHERE ref = ?"
        cursor.execute(query, (peso, ref))
        conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao atualizar peso: {e}")
        return False

import mysql.connector  # Importa o mysql-connector-python
import pyodbc
import tempfile
import os
import logging

logger = logging.getLogger(__name__)
import pyodbc
from .models import HelpTopicLabelMapping
import logging

logger = logging.getLogger(__name__)

def obter_label_id_por_help_topic(help_topic_id):
    try:
        # Busca o label_id associado ao help_topic_id
        label_mapping = HelpTopicLabelMapping.objects.get(help_topic_id=help_topic_id)
        return label_mapping.label_id
    except HelpTopicLabelMapping.DoesNotExist:
        logger.error("Label ID não encontrado para o help_topic_id: %s", help_topic_id)
        return None

import mysql.connector

def obter_configuracao_por_id(label_id):
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
        cursor = conn.cursor()
        
        query_sql = """
        SELECT query, zpl 
        FROM [PHCTRI].[dbo].[u_labels_alb]
        WHERE id = ?
        """
        
        cursor.execute(query_sql, (label_id,))
        result = cursor.fetchone()
        
        if result:
            query_text, zpl_template = result
            queries = query_text.split(';')
            return queries, zpl_template
        else:
            logger.error("Configuração não encontrada para o label_id: %s", label_id)
            return None, None
    
    except Exception as e:
        logger.error(f"Erro ao buscar a configuração: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def obter_dados_ticket(ticket_id, queries):
    try:
        # Conectar ao banco de dados do osTicket
        db = mysql.connector.connect(
            host="192.168.120.106",
            user="root",
            password="tri123",
            database="osticket_db",
            charset="utf8"
        )
        cursor = db.cursor()

        # Executar a primeira consulta (dados fixos)
        cursor.execute(queries[0], (ticket_id,))
        dados_fixos = cursor.fetchone()  # Deve ser uma tupla

        logger.debug(f"Dados fixos retornados: {dados_fixos} (Tipo: {type(dados_fixos)})")

        if not dados_fixos:
            raise ValueError("Nenhum dado fixo retornado pela consulta.")
        
        if not isinstance(dados_fixos, tuple):
            raise ValueError(f"Formato de dados fixos inesperado: {type(dados_fixos)}")
        
        if len(dados_fixos) != 3:
            raise ValueError(f"Quantidade inesperada de elementos em dados_fixos: {len(dados_fixos)}")
        
        ticket_number, help_topic_id, help_topic = dados_fixos
        
        # Executar a segunda consulta (dados variáveis)
        cursor.execute(queries[1], (ticket_id,))
        resultados_variaveis = cursor.fetchall()  # Deve ser uma lista de tuplas

        logger.debug(f"Resultados variáveis retornados: {resultados_variaveis} (Tipo: {type(resultados_variaveis)})")

        return (ticket_number, help_topic_id, help_topic), resultados_variaveis
    
    except Exception as e:
        logger.error(f"Erro ao obter dados do ticket: {e}")
        return None, None
    finally:
        cursor.close()
        db.close()

def gerar_zpl(ticket_id, dados_fixos, resultados_variaveis, zpl_template):
    logger.debug("Iniciando a geração do ZPL")

    if not dados_fixos or not resultados_variaveis:
        logger.error("Dados insuficientes para gerar o ZPL.")
        return None

    ticket_number, help_topic_id, help_topic = dados_fixos

    qrcode_link = f"http://192.168.120.106/scp/tickets.php?id={ticket_id}"


    data = {
        'ticket_number': ticket_number,
        'help_topic': help_topic,
        'QRCode': qrcode_link  # Adicionar o QR Code aos dados

    }

    for row in resultados_variaveis:
        if len(row) == 2:
            label, value = row
            clean_label = label.replace(" ", "_").replace(":", "").replace("(", "").replace(")", "").replace("'", "").replace('"', '')
            data[clean_label] = value
        else:
            logger.error(f"Formato de dados variáveis inesperado: {row} (Tipo: {type(row)})")

    logger.debug("Data collected: %s", data)

    verificar_placeholders(zpl_template, data.keys())

    zpl_final = zpl_template
    for key, value in data.items():
        placeholder = f'{{{key}}}'
        if placeholder in zpl_final:
            zpl_final = zpl_final.replace(placeholder, str(value))
        else:
            logger.warning(f"Placeholder {placeholder} não encontrado no template.")

    logger.debug("ZPL Final: %s", zpl_final)

    with open(f'zpl_output_{ticket_id}.txt', 'w', encoding='utf-8') as file:
        file.write(zpl_final)

    return zpl_final



def verificar_placeholders(template, keys):
    placeholders = ['ticket_number', 'help_topic'] + [f"{key}" for key in keys]
    for placeholder in placeholders:
        if f'{{{placeholder}}}' not in template:
            logger.error(f"Placeholder {{{placeholder}}} não encontrado no template.")


def obter_ip_impressora():
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
        cursor = conn.cursor()
        query = "SELECT ip FROM u_printers_alb WHERE id = 47"
        cursor.execute(query)
        row = cursor.fetchone()
        
        if row:
            return row.ip
        else:
            return None
        
    except Exception as e:
        logger.error(f"Erro ao buscar a impressora: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def obter_help_topic_id_do_ticket(ticket_id):
    try:
        # Conectar ao banco de dados do osTicket
        db = mysql.connector.connect(
            host="192.168.120.106",  
            user="root",        
            password="tri123",      
            database="osticket_db",     
            charset="utf8"
        )
        
        cursor = db.cursor()
        
        # Executar a consulta para obter o help_topic_id
        query = """
        SELECT oht.topic_id
        FROM ost_help_topic oht
        INNER JOIN ost_ticket ot ON ot.topic_id = oht.topic_id
        WHERE ot.ticket_id = %s
        """
        
        cursor.execute(query, (ticket_id,))
        result = cursor.fetchone()
        
        cursor.close()
        db.close()
        
        if result:
            return result[0]  # Retorna o help_topic_id
        else:
            return None  # Retorna None se nenhum resultado for encontrado
    
    except Exception as e:
        logger.error(f"Erro ao obter o help_topic_id: {e}")
        return None

def formatar_descricao(descricao, largura_max=32):
    """
    Formata a descrição para garantir que não exceda o comprimento máximo e adiciona quebras de linha.
    """
    descricao = descricao.replace('<p>', '').replace('</p>', '')  # Remover tags HTML
    linhas = []
    palavras = descricao.split()
    
    linha_atual = ""
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 <= largura_max:
            if linha_atual:
                linha_atual += " "
            linha_atual += palavra
        else:
            linhas.append(linha_atual)
            linha_atual = palavra
    
    if linha_atual:
        linhas.append(linha_atual)
    
    return "\n".join(linhas)

