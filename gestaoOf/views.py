import datetime
from django.shortcuts import render
import pyodbc
import logging
import time
from datetime import datetime, timedelta

loggy = logging.getLogger(__name__)


# Configurar logging
logging.basicConfig(
    level=logging.INFO,  # Você pode usar DEBUG para mais detalhes
    format='%(asctime)s - %(levelname)s - %(message)s',
)
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=192.168.120.9;'
    'DATABASE=PHCTRI;'
    'UID=estagio;'
    'PWD=3stAg10..;'
    )



def producao_view(request):
    # Conectar ao SQL Server
    logging.info(f"Parâmetros recebidos: {request.GET}")


    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=192.168.120.9;'
        'DATABASE=PHCTRI;'
        'UID=estagio;'
        'PWD=3stAg10..;'
        )
#se a conexão estiver fechada abrir a conexão
    if conn.closed:
        conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=192.168.120.9;'
        'DATABASE=PHCTRI;'
        'UID=estagio;'
        'PWD=3stAg10..;'
        )
        logging.info('Conexão reaberta')
    else:
        logging.info('Conexão aberta')
        
    cursor = conn.cursor()    
    # Inicializar filtros
    marca = request.GET.get('marca')
    modelo = request.GET.get('modelo')
    tamanho = request.GET.get('tamanho')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim', '')
    nave = request.GET.getlist('nave')
    of_mae = request.GET.getlist('of_mae')
    
    #de hoje a menso de 60 dias
    
    data_2_meses_atras = datetime.now() - timedelta(days=60)
    data_2_meses_atras = data_2_meses_atras.strftime('%Y-%m-%d')
    loggy.info(f"Data 2 meses atrás: {data_2_meses_atras}")
    

    # Naves
    cursor.execute("SELECT DISTINCT nave FROM u_prod_work_center_alb WHERE nave IS NOT NULL and nave > 0 ORDER BY nave")
    naves = [row[0] for row in cursor.fetchall()]

    # Marcas (sem depender da nave)
    cursor.execute("SELECT DISTINCT trim(usr1) FROM st ORDER BY trim(usr1)")
    marcas = [row[0] for row in cursor.fetchall()]
    
        # OFs Mãe onde data_entrega < ultimos dois meses
        
    cursor.execute("""
        SELECT DISTINCT obrano_fo, id, data_entrega
        FROM u_fo_alb
        WHERE ofparent IS NULL
        AND TRY_CONVERT(DATE, CONCAT(SUBSTRING(data_entrega, 7, 4), '-', SUBSTRING(data_entrega, 4, 2), '-', SUBSTRING(data_entrega, 1, 2)), 120) >= CAST(DATEADD(DAY, -60, GETDATE()) AS DATE)
        AND status IN (2, 4)
        AND conversao = 0
        ORDER BY obrano_fo

    """)

    of_mae_list = cursor.fetchall()    #guardar vo obrano_fo e id
    logging.info(f"OF Mãe List: {of_mae_list}")



    modelos = []
    if marca:
        cursor.execute("SELECT DISTINCT trim(usr2) FROM st WHERE usr1 = ? ORDER BY trim(usr2)", (marca,))
        modelos = [row[0] for row in cursor.fetchall()]

    tamanhos = []
    if modelo:
        cursor.execute("SELECT DISTINCT trim(u_tamanho) FROM st WHERE usr2 = ? ORDER BY trim(u_tamanho)", (modelo,))
        tamanhos = [row[0] for row in cursor.fetchall()]


    data = None
    data_list = []
    
    if marca or modelo or tamanho or data_inicio or data_fim or nave or of_mae:
        # Montar query principal com filtros
        query = """
            SELECT 
                parent_st.usr1 AS MARCA, 
                parent_st.usr2 AS MODELO, 
                parent_st.u_tamanho AS Size, 
                u_fo_alb.qtt_real AS Qt, 
                u_fo_alb.ofparent AS OFMae, 
                u_fo_alb.sequencial AS Obs, 
                u_fo_alb.data_entrega AS Entrega, 
                u_prod_work_center_alb.nave AS Nave,
                u_fo_alb.obrano_fo AS SubOF, 
				u_fo_alb.prox,
                st.lang4 AS COMPONENTE, 
                u_sections_alb.name AS Seccao, 
                st.design AS Descricao, 
                u_fo_alb.ref, 
                u_fo_alb.qtt_real AS Pedido, 
                u_fo_alb.qtt_produzida, 
                u_fo_alb.qtt_rejeitada,
                u_fo_alb.id as of_id

            FROM 
                u_fo_alb
            INNER JOIN 
                st ON u_fo_alb.ref = st.ref
            Inner JOIN 
                u_prod_work_center_alb ON u_prod_work_center_alb.design = u_fo_alb.ct_design
            INNER JOIN 
                u_sections_alb ON u_sections_alb.id = u_prod_work_center_alb.id_section
            LEFT JOIN 
                u_fo_alb parent_fo ON parent_fo.id = u_fo_alb.ofparent
            LEFT JOIN 
                st parent_st ON parent_fo.ref = parent_st.ref
            WHERE 
                u_fo_alb.status in (2, 4) 
                AND u_fo_alb.conversao = 0
        """

        # Adicionar filtros à query
        if marca:
            query += f" AND parent_st.usr1 = '{marca}'"
        if modelo:
            query += f" AND parent_st.usr2 = '{modelo}'"
        if tamanho:
            query += f" AND parent_st.u_tamanho = '{tamanho}'"
        if data_inicio and data_fim:
            query += f" AND u_fo_alb.data_entrega BETWEEN '{data_inicio}' AND '{data_fim}'"
        if nave:
            nave_filter = ",".join([f"'{n}'" for n in nave])
            query += f" AND u_prod_work_center_alb.nave IN ({nave_filter})"
        if of_mae:
            of_mae_filter = ",".join([f"'{n}'" for n in of_mae])
            query += f" AND u_fo_alb.ofparent IN ({of_mae_filter})"


        query += "ORDER BY parent_st.usr1, parent_st.usr2, parent_st.u_tamanho, u_fo_alb.ofparent, st.lang4, u_fo_alb.prox"
        
        logging.info(f"Query: {query}")
        
        #fazer um array com as ofmae do resultado
        
        # Executar a query
        cursor.execute(query)
        
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Organizar dados por OF Mãe e SubOFs
        data = {}
        for row in rows:
            ofmae = row['OFMae']

            # Substituir OFMae pelo valor de obrano_fo
            cursor.execute(f"SELECT obrano_fo FROM u_fo_alb WHERE id = ?", (ofmae,))
            obrano_fo = cursor.fetchone()
            if obrano_fo:
                ofmae = obrano_fo[0]  # Substituir OFMae pelo valor de obrano_fo

            # Organizar dados no dicionário
            if ofmae not in data:
                data[ofmae] = {
                    'MARCA': row['MARCA'],
                    'MODELO': row['MODELO'],
                    'Size': row['Size'],
                    'Qt': row['Qt'],
                    'Obs': row['Obs'],     
                    'Entrega': row['Entrega'],
                    'ID': row['OFMae'],
                    'SubOFs': []
                }
                
                # Calcular a porcentagem do processo
            pedido = row['Pedido'] if row['Pedido'] is not None else 0  # Verificar se 'Pedido' é None
            produzida = row['qtt_produzida'] if row['qtt_produzida'] is not None else 0
            rejeitada = row['qtt_rejeitada'] if row['qtt_rejeitada'] is not None else 0

            # Evitar divisão por zero e garantir que 'pedido' seja maior que zero
            processo = 0
            if pedido > 0:
                processo = ((produzida - rejeitada) / pedido) * 100
                

            
            # Adicionar SubOFs
            data[ofmae]['SubOFs'].append({
                'SubOF': row['SubOF'],
                'COMPONENTE': row['COMPONENTE'],
                'Descricao': row['Descricao'],
                'Pedido': row['Pedido'],
                'Produzida': row['qtt_produzida'],
                'Rejeitada': row['qtt_rejeitada'],
                'Seccao': row['Seccao'],
                'Ref': row['ref'],
                'Processo': round(processo, 2),  # Exibindo o processo com 2 casas decimais
                'ID': row['of_id'],
                'OFMae': row['OFMae'],
                

                
            })
            
        data_list = [{'OFMae': key, **value} for key, value in data.items()]

        # Paginação

    else:
        conn.close()
    
    
    #data de hoje
    data_inicio = time.strftime('%Y-%m-%d')
    #data de hoje mais uma semana
    data_fim = time.strftime('%Y-%m-%d', time.localtime(time.time() + 604800))
    



    return render(request, 'gestaoOf/producao.html', {
        'page_title': 'Gestão de OF\u00F5s',
        'marcas': marcas,
        'modelos': modelos,
        'tamanhos': tamanhos,
        'naves': naves,
        'of_mae_list': of_mae_list,
        'data': data_list,  # page_obj pode ser None ou uma página de dados
        'marca': marca,
        'modelo': modelo,
        'tamanho': tamanho,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'nave': nave,
        'of_mae': of_mae,

    })



from django.http import JsonResponse

conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=192.168.120.9;'
        'DATABASE=PHCTRI;'
        'UID=estagio;'
        'PWD=3stAg10..;'
    )
cursor = conn.cursor()

def get_marcas(request):
    of_mae = request.GET.get('of_mae')
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=192.168.120.9;'
        'DATABASE=PHCTRI;'
        'UID=estagio;'
        'PWD=3stAg10..;'
    )
    cursor = conn.cursor()

    if not of_mae:
        # Se nenhuma OF Mãe foi selecionada, buscar todas as marcas
        cursor.execute("SELECT DISTINCT trim(usr1) FROM st ORDER BY usr1")
    else:
        # Buscar marcas baseadas na OF Mãe selecionada
        cursor.execute("SELECT DISTINCT trim(usr1) FROM st WHERE ref IN (SELECT ref FROM u_fo_alb WHERE ofparent = ?) ORDER BY usr1", (of_mae,))

    marcas = [row[0] for row in cursor.fetchall()]
    conn.close()

    return JsonResponse({'marcas': marcas})

def get_modelos(request):
    marca = request.GET.get('marca')
    modelos = []
    if marca:
        cursor.execute("SELECT DISTINCT trim(usr2) FROM st WHERE usr1 = ? ORDER BY trim(usr2)", (marca,))
        modelos = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'modelos': modelos})


def get_tamanhos(request):
    modelo = request.GET.get('modelo')
    tamanhos = []
    if modelo:
        cursor.execute("SELECT DISTINCT trim(u_tamanho) FROM st WHERE usr2 = ? ORDER BY u_tamanho", (modelo,))
        tamanhos = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'tamanhos': tamanhos})


from django.http import JsonResponse
from django.db import connection

def get_sorted_subofs(request):
    try:
        ofmae_id = request.GET.get('ofmae_id', None)
        if not ofmae_id:
            return JsonResponse({'error': 'ofmae_id é necessário'}, status=400)

        # Aqui você pode executar as queries usando a conexão
        cursor = conn.cursor()
        
        # Consulta de exemplo
        cursor.execute(f"""
            select obrano_fo, ref, operation_name, id, prox
            into #tempof
            from u_fo_alb
            where ofparent = {ofmae_id} and prox in (select id from u_fo_alb)
        """)
        
        cursor.execute("""
            select a.obrano_fo, a.ref, c.design, a.operation_name, a.id, a.prox,
                   b.obrano_fo, b.operation_name, b.nivel,
                   c.lang4, d.nave
            from #tempof a
            left join u_fo_alb b on a.prox = b.id
            inner join st c on c.ref = a.ref
            inner join u_prod_work_center_alb d on d.id = b.ct_id
            where nave in (1, 5, 2)
            order by lang4, prox desc
        """)
        
        # Processar os dados retornados pela consulta
        result = cursor.fetchall()
        
        subof_data = []
        for row in result:
            subof_data.append({
                'obrano_fo': row.obrano_fo,
                'ref': row.ref,
                'operation_name': row.operation_name,
                'id': row.id,
                'prox': row.prox,
                'nave': row.nave,
            })
        
        return JsonResponse({'subofs': subof_data})
    except pyodbc.Error as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        cursor.close()