from django.shortcuts import render
import pyodbc
import logging
import time

# Configurar logging
logging.basicConfig(
    level=logging.INFO,  # Você pode usar DEBUG para mais detalhes
    format='%(asctime)s - %(levelname)s - %(message)s',
)



def producao_view(request):
    # Conectar ao SQL Server
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=SERVER;'
        'DATABASE=DB;'
        'UID=user;'
        'PWD=pass..;'
    )
    cursor = conn.cursor()
    
    # Inicializar filtros
    marca = request.GET.get('marca', '')
    modelo = request.GET.get('modelo', '')
    tamanho = request.GET.get('tamanho', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')
    nave = request.GET.get('nave', '').strip()
    of_mae = request.GET.get('of_mae', '')



    # Naves
    cursor.execute("SELECT DISTINCT nave FROM u_prod_work_center_alb WHERE nave IS NOT NULL ORDER BY nave")
    naves = [row[0] for row in cursor.fetchall()]

    # Marcas (sem depender da nave)
    cursor.execute("SELECT DISTINCT usr1 FROM st ORDER BY usr1")
    marcas = [row[0] for row in cursor.fetchall()]
    
        # OFs Mãe
    cursor.execute("SELECT DISTINCT ofparent FROM u_fo_alb WHERE ofparent IS NOT NULL ORDER BY ofparent")
    of_mae_list = [row[0] for row in cursor.fetchall()]


    modelos = []
    if marca:
        cursor.execute("SELECT DISTINCT usr2 FROM st WHERE usr1 = ? ORDER BY usr2", (marca,))
        modelos = [row[0] for row in cursor.fetchall()]

    tamanhos = []
    if modelo:
        cursor.execute("SELECT DISTINCT u_tamanho FROM st WHERE usr2 = ? ORDER BY u_tamanho", (modelo,))
        tamanhos = [row[0] for row in cursor.fetchall()]


    data = None
    data_list = []
    
    if marca or modelo or tamanho or data_inicio or data_fim or nave:
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
            query += f" AND u_prod_work_center_alb.nave = '{nave}'"
        if of_mae:
            query += f" AND u_fo_alb.ofparent = '{of_mae}'"


        query += " ORDER BY parent_st.usr1, parent_st.usr2, parent_st.u_tamanho, u_fo_alb.ofparent, u_fo_alb.obrano_fo"
        
        #obter os ids da of mae, por em um array, e fazer a query temporaria e depois ordernar a query anterior por esse array

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
                    'ID': row['of_id'],
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
            
        # Ordenar as OFs Mãe pela data de entrega
        data_list = sorted(
            [{'OFMae': key, **value} for key, value in data.items()],
            key=lambda x: x['Entrega'],  # Ordenar por data de entrega
        )
        
        
        # Ordenar as SubOFs de cada OF Mãe
        for ofmae_data in data_list:
            ofmae_id = ofmae_data['OFMae']
            
            # Executar a consulta para ordenar as SubOFs
            cursor.execute(f"""
                SELECT a.obrano_fo, a.ref, c.design, a.operation_name, a.id, a.prox,
                    b.obrano_fo AS prox_obrano_fo, b.operation_name AS prox_operation_name,
                    b.nivel, c.lang4, d.nave
                FROM u_fo_alb a
                LEFT JOIN u_fo_alb b ON a.prox = b.id
                INNER JOIN st c ON c.ref = a.ref
                INNER JOIN u_prod_work_center_alb d ON d.id = b.ct_id
                WHERE a.ofparent = ? AND d.nave IN (1, 5, 2)
                ORDER BY c.lang4, a.prox DESC
            """, (ofmae_id,))

            subofs_rows = cursor.fetchall()

            # Organizar e adicionar as SubOFs na OF Mãe
            subofs = []
            for subof_row in subofs_rows:
                subofs.append({
                    'SubOF': subof_row.obrano_fo,
                    'COMPONENTE': subof_row.lang4,
                    'Descricao': subof_row.operation_name,
                    'Pedido': subof_row.prox,  # Caso necessário adaptar a lógica de 'Pedido'
                    'Produzida': subof_row.nivel,  # Caso necessário adaptar a lógica de 'Produzida'
                    'Rejeitada': 0,  # Ajuste conforme necessário
                    'Seccao': subof_row.design,
                    'Ref': subof_row.ref,
                    'Processo': 0,  # Calcule o processo conforme necessário
                    'ID': subof_row.id,
                    'OFMae': ofmae_id,
                })
            
            # Substitua ou adicione a lista de SubOFs ordenadas para cada OF Mãe
            ofmae_data['SubOFs'] = subofs

        # Caso não haja filtros, não há dados para paginar

    conn.close()
    
    
    #data de hoje
    data_inicio = time.strftime('%Y-%m-%d')
    #data de hoje mais uma semana
    data_fim = time.strftime('%Y-%m-%d', time.localtime(time.time() + 604800))

    return render(request, 'gestaoOf/producao.html', {
        'marcas': marcas,
        'modelos': modelos,
        'tamanhos': tamanhos,
        'naves': naves,
        'of_mae_list': of_mae_list,
        'data': data_list,  # page_obj pode ser None ou uma página de dados
        'filtros': {'marca': marca, 'modelo': modelo, 'tamanho': tamanho, 'data_inicio': data_inicio, 'data_fim': data_fim, 'nave': nave,  'of_mae': of_mae},
    })



from django.http import JsonResponse

conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=SERVER;'
        'DATABASE=DB;'
        'UID=user;'
        'PWD=pass..;'
    )
cursor = conn.cursor()

def get_marcas(request):
    of_mae = request.GET.get('of_mae')
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=SERVER;'
        'DATABASE=DB;'
        'UID=user;'
        'PWD=pass..;'
    )
    cursor = conn.cursor()

    if not of_mae:
        # Se nenhuma OF Mãe foi selecionada, buscar todas as marcas
        cursor.execute("SELECT DISTINCT usr1 FROM st ORDER BY usr1")
    else:
        # Buscar marcas baseadas na OF Mãe selecionada
        cursor.execute("SELECT DISTINCT usr1 FROM st WHERE ref IN (SELECT ref FROM u_fo_alb WHERE ofparent = ?) ORDER BY usr1", (of_mae,))

    marcas = [row[0] for row in cursor.fetchall()]
    conn.close()

    return JsonResponse({'marcas': marcas})

def get_modelos(request):
    marca = request.GET.get('marca')
    modelos = []
    if marca:
        cursor.execute("SELECT DISTINCT usr2 FROM st WHERE usr1 = ? ORDER BY usr2", (marca,))
        modelos = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'modelos': modelos})


def get_tamanhos(request):
    modelo = request.GET.get('modelo')
    tamanhos = []
    if modelo:
        cursor.execute("SELECT DISTINCT u_tamanho FROM st WHERE usr2 = ? ORDER BY u_tamanho", (modelo,))
        tamanhos = [row[0] for row in cursor.fetchall()]
    return JsonResponse({'tamanhos': tamanhos})