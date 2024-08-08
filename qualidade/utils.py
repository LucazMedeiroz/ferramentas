


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















    


