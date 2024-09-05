import pyodbc
from datetime import datetime, timedelta
import pyodbc
from datetime import datetime, timedelta

def producao(seccao=None, marca=None, modelo=None, componente=None, ct_design=None, start_date=None, end_date=None, incluir_semana_passada=False):
    import pyodbc

    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()

    # Construir a parte da consulta SQL para os filtros
    filter_conditions = []
    params = []
    if seccao:
        filter_conditions.append("u_sections_alb.name = ?")
        params.append(seccao)
    if marca:
        filter_conditions.append("st.usr1 = ?")
        params.append(marca)
    if modelo:
        filter_conditions.append("st.usr2 = ?")
        params.append(modelo)
    if componente:
        filter_conditions.append("st.lang4 = ?")
        params.append(componente)
    if ct_design:
        filter_conditions.append("u_fo_alb.ct_design = ?")
        params.append(ct_design)

    # Concatenar as condições de filtro
    where_clause = ""
    if filter_conditions:
        where_clause = "WHERE " + " AND ".join(filter_conditions)

    # Adicionar as condições de data se fornecidas
    if start_date and end_date:
        where_clause += " AND u_shopfloor_alb.final >= ? AND u_shopfloor_alb.final <= ?"
        params.extend([start_date, end_date])

    elif start_date:
        where_clause += " AND u_shopfloor_alb.final >= ?"
        params.append(start_date)
    
    elif end_date:
        where_clause += " AND u_shopfloor_alb.final <= ?"
        params.append(end_date)

    query = f"""
    SELECT SUM(u_shopfloor_alb.qtt - u_shopfloor_alb.rejected) AS PRODUCAO,
           st.ref, st.design, st.usr1, st.usr2, st.lang4, st.lang5, st.u_nave, st.u_tamanho,
           u_fo_alb.ct_design, u_sections_alb.name, u_shopfloor_alb.final
    FROM u_shopfloor_alb
    INNER JOIN u_fo_alb ON u_shopfloor_alb.id_fo = u_fo_alb.id
    INNER JOIN st ON u_fo_alb.ref = st.ref
    INNER JOIN u_prod_work_center_alb ON u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
    INNER JOIN u_sections_alb ON u_prod_work_center_alb.id_section = u_sections_alb.id
    {where_clause}
    AND u_shopfloor_alb.rework = 0
    GROUP BY st.ref, st.design, st.usr1, st.usr2, st.lang4, st.lang5, st.u_nave, st.u_tamanho,
             u_fo_alb.ct_design, u_sections_alb.name, u_shopfloor_alb.final
    ORDER BY PRODUCAO DESC
    """



    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Construindo a lista de dicionários para os resultados
    results = []
    for row in rows:
        result_dict = {
            'producao': row[0],
            'ref': row[1],
            'design': row[2],
            'usr1': row[3],
            'usr2': row[4],
            'lang4': row[5],
            'lang5': row[6],
            'u_nave': row[7],
            'u_tamanho': row[8],
            'ct_design': row[9],
            'name': row[10],
            'final': row[11]
        }
        results.append(result_dict)

    cursor.close()
    conn.close()
    return results


import pyodbc
from datetime import datetime, timedelta

def get_unique_values(column, filter_column=None, filter_value=None):
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    if filter_column and filter_value:
        query = f"SELECT DISTINCT {column} FROM st WHERE {filter_column} = ? ORDER BY {column}"
        cursor.execute(query, (filter_value,))
    else:
        query = f"SELECT DISTINCT {column} FROM st ORDER BY {column}"
        cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [row[0] for row in rows]


def get_seccoes():
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT u_sections_alb.name 
        FROM u_sections_alb 
        INNER JOIN u_prod_work_center_alb 
        ON u_prod_work_center_alb.id_section = u_sections_alb.id
    """)
    rows = cursor.fetchall()
    sections = [row[0] for row in rows]
    cursor.close()
    conn.close()
    return sections

def get_marcas(seccao=None):
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()

    if seccao:
        cursor.execute("""
            SELECT DISTINCT st.usr1
            FROM u_shopfloor_alb
            INNER JOIN u_fo_alb ON u_shopfloor_alb.id_fo = u_fo_alb.id
            INNER JOIN st ON u_fo_alb.ref = st.ref
            INNER JOIN u_prod_work_center_alb ON u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
            INNER JOIN u_sections_alb ON u_prod_work_center_alb.id_section = u_sections_alb.id
            WHERE u_sections_alb.name = ?
              AND u_shopfloor_alb.rework = 0
        """, (seccao,))
    else:
        cursor.execute("""
            SELECT DISTINCT st.usr1
            FROM u_shopfloor_alb
            INNER JOIN u_fo_alb ON u_shopfloor_alb.id_fo = u_fo_alb.id
            INNER JOIN st ON u_fo_alb.ref = st.ref
            INNER JOIN u_prod_work_center_alb ON u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
            INNER JOIN u_sections_alb ON u_prod_work_center_alb.id_section = u_sections_alb.id
            WHERE u_shopfloor_alb.rework = 0
        """)

    rows = cursor.fetchall()
    marcas = [row[0] for row in rows]

    cursor.close()
    conn.close()
    return marcas





def get_modelos(marca=None):
    return get_unique_values('usr2', 'usr1', marca)

def get_componentes(modelo=None):
    return get_unique_values('lang4', 'usr2', modelo)

def get_ct_designs(seccao=None):
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()

    if seccao:
        cursor.execute("""
            SELECT DISTINCT u_fo_alb.ct_design
            FROM u_shopfloor_alb
            INNER JOIN u_fo_alb ON u_shopfloor_alb.id_fo = u_fo_alb.id
            INNER JOIN u_prod_work_center_alb ON u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
            INNER JOIN u_sections_alb ON u_prod_work_center_alb.id_section = u_sections_alb.id
            WHERE u_sections_alb.name = ?
        """, (seccao,))
    else:
        cursor.execute("""
            SELECT DISTINCT u_fo_alb.ct_design
            FROM u_shopfloor_alb
            INNER JOIN u_fo_alb ON u_shopfloor_alb.id_fo = u_fo_alb.id
            INNER JOIN u_prod_work_center_alb ON u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
        """)

    rows = cursor.fetchall()
    ct_designs = [row[0] for row in rows]
    

    cursor.close()
    conn.close()
    return ct_designs

#------------------------------------------------------------------------------
# FunÇÕES PARA AS PÁGINAS DE CORTE E LASER

import pyodbc

def get_of_id(of):
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    query = f"SELECT id FROM u_fo_alb WHERE obrano_fo = '{of}'"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows[0][0] if rows else None

def get_of_details(of):
    id = get_of_id(of)
    if id is None:
        return []

    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    query = f"""
        SELECT 
            u_fo_alb.obrano_fo,
            u_fo_alb.qtt_real,
            u_fo_alb.qtt_produzida,
            bi.ref,
            bi.design,
            bi.qtt,
            st.unidade,
            u_fo_alb.status

        FROM u_fo_alb
        INNER JOIN bi ON u_fo_alb.reserva = bi.bostamp
        INNER JOIN st ON bi.ref = st.ref
        WHERE ofparent = '{id}' AND operation_id IN (100, 101)
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_material(obrano_fo):
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    query = f"""
        SELECT 
            st.design,
            (u_fo_alb.qtt_real - u_fo_alb.qtt_produzida) AS FALTA,

            st.u_lenght
        FROM u_fo_alb
        INNER JOIN st ON st.ref = u_fo_alb.ref
        WHERE obrano_fo = '{obrano_fo}'
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_componente(ref):
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    cursor.execute("SELECT lang4 FROM st WHERE ref = ?", ref)  
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows[0][0] if rows else None


