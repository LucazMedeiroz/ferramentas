from turtle import pd
import pyodbc
from collections import defaultdict
from datetime import datetime

def encomendasAbertasUtils(data_inicio=None, data_fim=None, cliente=None, marca=None, modelo=None):
    print('-----------------------------------------------------------------------------------------------------------------------------------------------')
    # Logs iniciais
    print('data_inicio:', data_inicio)
    print('data_fim:', data_fim)
    print('cliente:', cliente)
    print('marca:', marca)
    print('modelo:', modelo)
    
    # Definição da query base
    query_base = """
-- Subquery para obter a última data de atualização do inventário
WITH last_stock_date AS (
    SELECT MAX(CONVERT(date, CONCAT(ANO, '-', MES, '-', DIA))) AS last_date
    FROM u_stock_diario
)

-- Query principal
SELECT 
    bi.obrano, 
    bi.ref, 
    bi.design, 
    st.usr1 AS MARCA, 
    st.usr2 AS MODELO, 
    bi.qtt, 
    bi.qtt2 AS entregue,
    (bi.qtt - bi.qtt2) AS em_aberto, 
    CONVERT(date, bi.rdata) AS data_para_entrega, 
    st.u_tamanho AS tamanho, 
    (bi.rdata - 1) as data_para_entrega_menos_um, 
    COALESCE(stock_info.STOCK, 0) AS quadro_stock, 
    stock_info.u_cor AS cor
FROM 
    bi WITH (NOLOCK)
INNER JOIN 
    st ON bi.ref = st.ref
LEFT JOIN (
    SELECT 
        u_stock_diario.ref, 
        st.u_cor, 
        SUM(u_stock_diario.stock) AS STOCK
    FROM 
        u_stock_diario WITH (NOLOCK)
    INNER JOIN 
        st ON u_stock_diario.ref = st.ref
    WHERE 
        COMPONENTE = 'QUADRO' 
        AND u_stock_diario.nave = 4
        AND CONVERT(date, CONCAT(ANO, '-', MES, '-', DIA)) = (SELECT last_date FROM last_stock_date)
    GROUP BY 

        u_stock_diario.ref, 
        st.u_cor
) AS stock_info 
    ON bi.ref = stock_info.ref
WHERE 
    bi.ndos = 29
    AND bi.fechada = 0 
    AND bi.qtt2 < bi.qtt



    """

    # Condições de filtro
    conditions = []
    parameters = []

    if data_inicio:
        conditions.append("bi.rdata >= ?")
        parameters.append(data_inicio)

    if data_fim:
        conditions.append("bi.rdata <= ?")
        parameters.append(data_fim)

    if cliente:
        conditions.append("bi.nome = ?")
        parameters.append(cliente)

    if marca:
        conditions.append("UPPER(TRIM(st.usr1)) = ?")
        parameters.append(marca.strip().upper())

    if modelo:
        conditions.append("UPPER(TRIM(st.usr2)) = ?")
        parameters.append(modelo.strip().upper())

    # Compondo a query final
    if conditions:
        query1 = query_base + " AND " + " AND ".join(conditions)
    else:
        query1 = query_base

    query1 += " ORDER BY bi.obrano ASC, bi.ref, data_para_entrega"

    # Log da query final
    print('query1:', query1)

    # Query para obter a última data de atualização do inventário
    query_get_last_date = """
        SELECT MAX(CONVERT(date, CONCAT(ANO, '-', MES, '-', DIA))) AS last_date
        FROM u_stock_diario
    """

    query2 = """
        SELECT nave, st.u_cor, SUM(sa.stock) as STOCK
        FROM u_stock_diario  WITH (NOLOCK)
        INNER JOIN st ON u_stock_diario.REF = st.ref
        INNER JOIN sa on u_stock_diario.REF = sa.ref
        WHERE COMPONENTE = 'QUADRO' AND CONVERT(date, CONCAT(ANO, '-', MES, '-', DIA)) = ? AND MARCA = ? AND MODELO = ? AND st.u_tamanho = ? and sa.armazem in (8, 35) 
        GROUP BY nave, st.u_cor
    """

    query2A = """

		select 
        ref,design,stock,usr1,lang4,lang5, u_nave as nave,
        from st where usr1= ? and usr2 = ?
 
 
select sum(stock) from st where u_nave = 4 and usr1='RIESE & MULLER      ' and usr2 like 'CARGO COMPACT24     %'


"""

    query_armazem = """
        SELECT ref, SUM(stock) as STOCK
        FROM sa  WITH (NOLOCK)
        WHERE armazem = 35 AND ref = ?
        GROUP BY ref
    """
    query_embalamento = """
        SELECT ref, SUM(stock) as STOCK
        FROM sa  WITH (NOLOCK)
        WHERE armazem = 8 AND ref = ?
        GROUP BY ref
    """

    query_embalamento2 = """
	   SELECT SUM(s.stock) as STOCK,  b.usr1, b.usr2, st.u_tamanho
        FROM sa s
		inner join bi b
		on b.ref = s.ref
        inner join st
        on st.ref = s.ref
        WHERE s.armazem = 8 and b.usr1 = ? and b.usr2 = ? and st.u_tamanho = ?
        GROUP BY  b.usr1, b.usr2, st.u_tamanho
        """

    query_estoque_detalhado = """
        SELECT    
          CASE 
        WHEN lang5 = '' THEN 'outros'
        ELSE lang5
    END AS  lang5, SUM(sa.stock) AS stock
        FROM st  WITH (NOLOCK)

        inner join sa on st.ref=sa.ref

        WHERE usr1 = ? AND usr2 = ? AND u_tamanho = ? AND u_nave = ? AND lang4 = 'QUADRO' and sa.armazem=8
        GROUP BY lang5
    """

    query_decapagem = """
        SELECT SUM(stock) as STOCK
        FROM sa  WITH (NOLOCK)
        WHERE armazem = 7 AND ref = ?

"""



    # Log das demais queries
    print('query_get_last_date:', query_get_last_date)
    print('query2:', query2)
    print('query_armazem:', query_armazem)
    print('query_estoque_detalhado:', query_estoque_detalhado)

    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    # Obter a última data de atualização do inventário
    cursor.execute(query_get_last_date)
    last_date_result = cursor.fetchone()
    last_date = last_date_result[0]

    print('--------------------------------LAST DATE----------------------------------------------')

    print(last_date)

    # Executar a consulta principal
    cursor.execute(query1, tuple(parameters))

    results = cursor.fetchall()

    columns = [column[0] for column in cursor.description]
    data = [dict(zip(columns, row)) for row in results]

    for row in data:
        cursor.execute(query2, '2024-07-22', row['MARCA'].strip(), row['MODELO'].strip(), row['tamanho'])
        estoques = cursor.fetchall()

        row['nave2'] = 0
        row['nave3'] = 0
        row['nave4'] = 0
        row['u_cor'] = []
        row['cores'] = []

        estoque_nave4 = 0

        for estoque in estoques:
            if estoque.nave == 2:
                row['nave2'] = estoque.STOCK
            elif estoque.nave == 3:
                row['nave3'] = estoque.STOCK
            elif estoque.nave == 4:
                estoque_nave4 += estoque.STOCK
                row['cores'].append({'cor': estoque.u_cor, 'stock': estoque.STOCK})

        row['nave4'] = estoque_nave4
        #cores da nave 4 que não foram pintados
        #qtt de quadros onde cor é null
        row['nave4_null'] = sum([c['stock'] for c in row['cores'] if c['cor'] == None])

        

        # Obter o estoque no armazém 35 para cada ref
        cursor.execute(query_armazem, row['ref'])
        armazem_result = cursor.fetchone()
        row['estoque_armazem'] = armazem_result.STOCK if armazem_result else 0

        row['total_entregue'] = sum([r['entregue'] for r in data])

        # Calcular o número da semana
        row['semana'] = row['data_para_entrega'].isocalendar()[1]

        cursor.execute(query_embalamento2, row['MARCA'].strip(), row['MODELO'].strip(), row['tamanho'].strip())
        embalamento = cursor.fetchall()
        row['embalamento'] = embalamento[0].STOCK if embalamento else 0

        cursor.execute(query_embalamento, row['ref'])
        embalamentoRef = cursor.fetchone()

        row['embalamentoRef'] = embalamentoRef.STOCK if embalamentoRef else 0



        estoques_detalhados = {2: {}, 3: {}, 4: {}}
        estoque3 = 0
        estoque4 = 0
        for nave in estoques_detalhados.keys():
            cursor.execute(query_estoque_detalhado, row['MARCA'].strip(), row['MODELO'].strip(), row['tamanho'].strip(), nave)
            detalhes_estoque = cursor.fetchall()
            for detalhe in detalhes_estoque:
                estoques_detalhados[nave][detalhe.lang5.strip()] = detalhe.stock
    
                if nave == 3:
                    estoque3 += detalhe.stock
                if nave == 4:
                    estoque4 += detalhe.stock

        
                    

                


        row['estoque_detalhado'] = estoques_detalhados
        row['estoque3'] = estoque3
        row['estoque4'] = estoque4

        # Log do estoque detalhado
        print('Estoque detalhado para', row['MARCA'], row['MODELO'], row['tamanho'])
        print(row['estoque_detalhado'])

    conn.close()

    grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))

    for row in data:
        marca = row['MARCA'].strip()
        modelo = row['MODELO'].strip()
        tamanho = row['tamanho'].strip()
        semana = row['semana']
        mes = row['data_para_entrega'].month
        ano = row['data_para_entrega'].year

        grouped_data[(semana, mes, ano)][marca][modelo][tamanho].append(row)
    #agrupar AS rows de detalhes e somar as quantidades, caso obrano, ref, design e data de entrega forem iguais:
    for semana, mes, ano in grouped_data.keys():
        for marca in grouped_data[(semana, mes, ano)].keys():
            for modelo in grouped_data[(semana, mes, ano)][marca].keys():
                for tamanho in grouped_data[(semana, mes, ano)][marca][modelo].keys():
                    rows = grouped_data[(semana, mes, ano)][marca][modelo][tamanho]
                    rows_agrupadas = []
                    for row in rows:
                        if not rows_agrupadas:
                            rows_agrupadas.append(row)
                        else:
                            for row_agrupada in rows_agrupadas:
                                if row['obrano'] == row_agrupada['obrano'] and row['ref'] == row_agrupada['ref'] and row['design'] == row_agrupada['design'] and row['data_para_entrega'] == row_agrupada['data_para_entrega']:
                                    row_agrupada['qtt'] += row['qtt']
                                    row_agrupada['entregue'] += row['entregue']
                                    row_agrupada['em_aberto'] += row['em_aberto']
                                    break
                            else:
                                rows_agrupadas.append(row)
                    grouped_data[(semana, mes, ano)][marca][modelo][tamanho] = rows_agrupadas
    


    final_data = []
    for (semana, mes, ano), marcas in grouped_data.items():
        for marca, modelos in marcas.items():
            for modelo, tamanhos in modelos.items():
                for tamanho, rows in tamanhos.items():
                    total_qtt = sum(row['qtt'] for row in rows)
                    total_em_aberto = sum(row['em_aberto'] for row in rows)
                    total_entregue = sum(row['entregue'] for row in rows)

                    # Calcular o estoque_armazem somando apenas uma vez por combinação única de ref e design
                    refs_designs_unicos = []
                    total_estoque_armazem = 0
                    total_emabalamento = 0
                    for row in rows:
                        ref_design = f"{row['ref']}_{row['design']}"
                        if ref_design not in refs_designs_unicos:
                            total_estoque_armazem += row['estoque_armazem']
                            total_emabalamento += row['embalamentoRef']
                            refs_designs_unicos.append(ref_design)

                    


                    
                    

                    final_data.append({
                        'semana': semana,
                        'mes': mes,
                        'ano': ano,
                        'MARCA': marca,
                        'MODELO': modelo,
                        'tamanho': tamanho,
                        'total_qtt': total_qtt,
                        'total_em_aberto': total_em_aberto,
                        'total_entregue': total_entregue,
                        'nave2': rows[0]['nave2'],
                        'nave3': rows[0]['nave3'],
                        'nave4': rows[0]['nave4'],
                        'nave4_null': rows[0]['nave4_null'],
                        #total do embalamento
                        'embalamento': rows[0]['embalamento'],
                        
                        'estoque_armazem': total_estoque_armazem,
                        'embalamentoRef': total_emabalamento,

                        'estoque_detalhado': rows[0]['estoque_detalhado'], 
                        'estoque3': rows[0]['estoque3'],
                        'estoque4': rows[0]['estoque4'],
                        'detalhes': rows,
                        #nave 2 
                        #'estoque_nave2': rows[0]['estoque_detalhado'][2],
                        #


                        'estoque_nave2': sum(rows[0]['estoque_detalhado'][2].values()),

                        # coluna para a cor que é null
                        'cor': None


                    })

    return final_data







def get_clientes_marcas_modelos():
    query = """
                SELECT 
                    UPPER(TRIM(nome)) as cliente,
                    UPPER(TRIM(usr1)) as marca,
                    UPPER(TRIM(usr2)) as modelo
                FROM 
                    bi  WITH (NOLOCK)
                WHERE 
                    ndos = 1
                GROUP BY 
                    UPPER(TRIM(nome)), 
                    UPPER(TRIM(usr1)), 
                    UPPER(TRIM(usr2))
                ORDER BY 
                    cliente ASC;


        
    """


    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()


    
    # Process the rows into a more usable structure
    results = []
    for row in rows:
        results.append({
            'cliente': row[0],
            'marca': row[1],
            'modelo': row[2],
        })
    return results

def salvar_detalhes_excel(data):
    writer = pd.ExcelWriter('detalhes.xlsx', engine='openpyxl')
    
    for idx, row in enumerate(data):
        detalhes_df = pd.DataFrame(row['detalhes'])
        detalhes_df.to_excel(writer, sheet_name=f'Detalhes {idx + 1}', index=False)
    
    writer.save()

    


#nave1
'''
import pyodbc

def fetch_id_versions():
    query = """
    SELECT id FROM u_prod_gama_versao_alb WHERE type IN (1,5,7) AND active = 1
    """
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return [row[0] for row in rows]

def fetch_marca_modelo_tamanho(main_ref):
    query = f"""
    SELECT st.usr1, st.usr2, st.u_tamanho FROM u_prod_gama_versao_alb a
    JOIN st ON a.main_ref = st.ref
    WHERE a.main_ref = '{main_ref}'
    """
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    print(row)  # Adicione isso para depuração
    return row[0], row[1], row[2]  # marca, modelo, tamanho


def fetch_nave1_data(id_version):
    query = f"""
    SELECT DISTINCT
        TRIM(lang4) AS lang4,
        b.u_nave,
        c.stock,
        d.obrano_fo,
        d.ofparent,
        d.status,
        d.qtt_real,
        d.qtt_produzida,
        TRIM(e.ref) AS ref,
        e.obrano_fo,
        e.status,
        e.sequencial,
        bi.qtt
    FROM u_prod_gama_operations_alb a
    INNER JOIN st b ON a.ref = b.ref
    INNER JOIN sa c ON b.ref = c.ref
    INNER JOIN u_fo_alb d ON a.ref = d.ref
    INNER JOIN u_fo_alb e ON d.ofparent = e.id
    left join bi
    on b.ref = bi.ref
    WHERE id_version = '{id_version}'
      AND b.u_nave = 1
      AND c.armazem = 8
      AND b.lang5 <> ''
      AND e.status = 2
      AND d.qtt_produzida > 0
    GROUP BY e.ref, lang4, b.u_nave, c.stock, d.obrano_fo, d.ofparent,
             d.status, d.qtt_real, d.qtt_produzida, e.ref, e.obrano_fo,
             e.status, e.sequencial, bi.qtt
    """
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Remove spaces in each field
    cleaned_rows = [
        (
            row[0].strip() if row[0] else None,  # lang4
            row[1],  # u_nave
            row[2],  # stock
            row[3],  # obrano_fo
            row[4],  # ofparent
            row[5],  # status
            row[6],  # qtt_real
            row[7],  # qtt_produzida
            row[8].strip() if row[8] else None,  # ref
            row[9],  # obrano_fo
            row[10],  # status
            row[11],  # sequencial
        )
        for row in rows
    ]
    return cleaned_rows


def generate_html_table(data):
    headers = ['ref', 'marca', 'modelo', 'tamanho', 'cs', 'ss', 'drp', 'mb', 'ht', 'dt', 'tt', 'st']
    lang4_keys = ['CS', 'SS', 'DT', 'MB', 'HT', 'TT', 'ST']

    html = '<table border="1">'
    html += '<thead><tr>'
    for header in headers:
        html += f'<th>{header}</th>'
    html += '</tr></thead><tbody>'

    for ref, details in data.items():
        marca, modelo, tamanho = fetch_marca_modelo_tamanho(ref)
        
        html += f'<tr><td>{ref}</td><td>{marca}</td><td>{modelo}</td><td>{tamanho}</td>'
        for lang4 in lang4_keys:
            value = details.get(lang4, 0)
            html += f'<td>{value}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    return html

def main():
    id_versions = fetch_id_versions()
    all_data = []
    
    for id_version in id_versions:
        rows = fetch_nave1_data(id_version)
        for row in rows:
            row_dict = {
                'ref': row[8],
                'lang4': row[0],
                'stock': row[2]
            }
            all_data.append(row_dict)
    
    # Organize data by 'ref' and then by 'lang4'
    organized_data = {}
    for entry in all_data:
        ref = entry['ref']
        lang4 = entry['lang4']
        stock = entry['stock']
        
        if ref not in organized_data:
            organized_data[ref] = {}
        
        organized_data[ref][lang4] = stock
    
    html = generate_html_table(organized_data)
    with open("output.html", "w") as f:
        f.write(html)

if __name__ == "__main__":
    main()

def fetch_nave1_data_nao_produzido(id_version):
    query = f"""
    SELECT DISTINCT
        TRIM(lang4) AS lang4,
        b.u_nave,
        SUM(c.stock) AS stock_nao_produzido,
        TRIM(b.usr1) AS marca,
        TRIM(b.usr2) AS modelo,
        TRIM(b.u_tamanho) AS tamanho
    FROM u_prod_gama_operations_alb a
    INNER JOIN st b ON a.ref = b.ref
    INNER JOIN sa c ON b.ref = c.ref
    WHERE id_version = '{id_version}'
      AND b.u_nave = 1
      AND c.armazem = 8
      AND b.lang5 = ''
      AND lang4 <> ''
    GROUP BY b.usr1, b.usr2, b.u_tamanho, b.u_nave, lang4
    """
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    cleaned_rows = [
        (
            row[0].strip() if row[0] else None,  # lang4
            row[2],  # stock_nao_produzido
            row[3],  # marca
            row[4],  # modelo
            row[5],  # tamanho
        )
        for row in rows
    ]
    return cleaned_rows




def fetch_all_marcas_modelos():
    query = """
    SELECT DISTINCT TRIM(usr1) AS marca, TRIM(usr2) AS modelo
    FROM st
    WHERE usr1 IS NOT NULL AND usr2 IS NOT NULL
    """
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    marcas_modelos = {}
    for row in rows:
        marca = row[0].strip()
        modelo = row[1].strip()
        if marca:
            if marca not in marcas_modelos:
                marcas_modelos[marca] = set()
            if modelo:
                marcas_modelos[marca].add(modelo)
    
    # Converte os sets para listas
    for marca in marcas_modelos:
        marcas_modelos[marca] = sorted(marcas_modelos[marca])

    return marcas_modelos

def fetch_marcas_por_tipo():
    query = """
    SELECT DISTINCT TRIM(st.usr1) AS marca, TRIM(st.usr2) AS modelo, TRIM(gt.name) AS tipo
    FROM st
    INNER JOIN u_prod_gama_versao_alb pgv ON pgv.main_ref = st.ref
    INNER JOIN u_gama_type_alb gt ON gt.id = pgv.type
    WHERE st.usr1 IS NOT NULL AND st.usr2 IS NOT NULL and gt.id in (1,5,7)
    """
    
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()

    marcas_por_tipo = {}

    for row in rows:
        marca = row[0].strip()
        modelo = row[1].strip()
        tipo = row[2].strip()

        if tipo not in marcas_por_tipo:
            marcas_por_tipo[tipo] = {}

        if marca not in marcas_por_tipo[tipo]:
            marcas_por_tipo[tipo][marca] = []

        marcas_por_tipo[tipo][marca].append(modelo)

    return marcas_por_tipo


    '''

def tipoGama():
    query = """
    SELECT id, type FROM u_prod_gama_versao_alb where type in (1,5,7)
    """
    conn_str = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..'
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

