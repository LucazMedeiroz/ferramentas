



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
    




import MySQLdb


def obter_dados_ticket(ticket_id):
    # Conectar ao banco de dados
    db = MySQLdb.connect(
        host="192.168.120.106",  
        user="root",        
        passwd="tri123",      
        db="osticket_db",     
        charset="utf8"
    )
    
    cursor = db.cursor()
    
    # Query para buscar as informações do ticket
    query = """

SELECT ot.`number` , oht.topic AS help_topic, off.label, ofev.value 
FROM ost_help_topic oht 
INNER JOIN ost_help_topic_form ohtf ON ohtf.topic_id = oht.topic_id 
INNER JOIN ost_ticket ot ON ot.topic_id = oht.topic_id 
INNER JOIN ost_form of ON of.id = ohtf.form_id 
INNER JOIN ost_form_field off ON off.form_id = ohtf.form_id 
INNER JOIN ost_form_entry_values ofev ON ofev.field_id = off.id 
WHERE ohtf.sort = 2 
 AND ot.ticket_id = %s
    """
    
    cursor.execute(query, (ticket_id,))
    
    results = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    return results


def gerar_zpl(ticket_id, resultados):
    # Código ZPL fixo com QR Code e texto ao lado
    zpl_fixo = """
    ^XA
    ^CI28          // Define a codificação UTF-8
    ^PW800
    ^LL560
    ^CF0,20

    // Define o QR Code com o link para o ticket na lateral direita
    ^FO400,20^BQN,2,10^FR^FDMA,http://192.168.120.106/scp/tickets.php?id={ticket_id}^FS

    // Define o texto ao lado do QR Code
    ^FO20,20^A0N,30,30^FDTicket #{ticket_number}^FS

    // Adiciona o Help Topic
    ^FO20,60^A0N,20,20^FDHelp Topic: {help_topic}^FS
    """
    
    # Adiciona labels e valores adicionais
    etiquetas = ""
    y_position = 100  # Ajustar a posição vertical conforme necessário
    

    ticket_number = ""  # Inicializa a variável ticket_number
    help_topic = ""  # Inicializa a variável help_topic
    
    for row in resultados:
        if len(row) != 4:
            raise ValueError("Resultado da consulta não está no formato esperado.")
        
        ticket_number, help_topic_db, label, value = row  # Desempacota os dados
        help_topic = help_topic_db  # Atualiza help_topic para o último valor encontrado
            
    for row in resultados:
        if len(row) != 4:
            raise ValueError("Resultado da consulta não está no formato esperado.")
        
        _, help_topic_db, label, value = row  # Desempacota os dados
        help_topic = help_topic_db  # Atualiza help_topic para o último valor encontrado
        
        # Substitua caracteres especiais se necessário
        label = label.replace('ç', 'c').replace('ã', 'a')  # Ajuste conforme necessário
        value = value.replace('ç', 'c').replace('ã', 'a')  # Ajuste conforme necessário
        
        etiquetas += "^FO20,{0}\n^A0N,20,20\n^FD{1}: {2}^FS\n".format(y_position, label, value)
        y_position += 40  # Ajusta a posição vertical para a próxima linha
    
    zpl_fixo += etiquetas + "^XZ"
    return zpl_fixo.format(ticket_id=ticket_id, ticket_number=ticket_number, help_topic=help_topic)


def obter_ip_impressora():
    try:
        conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
        cursor = conn.cursor()
        query = "SELECT ip FROM u_printers_alb WHERE id = 47"
        cursor.execute(query)
        row = cursor.fetchone()  # Fetch the first row
        
        if row:
            return row.ip  # Return the IP address
        else:
            return None  # Return None if no rows found
        
    except Exception as e:
        print(f"Erro ao buscar a impressora: {e}")
        return None

