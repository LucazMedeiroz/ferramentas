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
    
    logging.info("Iniciando a produção view")

    # Conectar ao SQL Server
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=192.168.120.9;'
            'DATABASE=PHCTRI;'
            'UID=estagio;'
            'PWD=3stAg10..;'
        )
        cursor = conn.cursor()
        logging.info("Conexão ao banco de dados estabelecida")
    except Exception as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return render(request, 'gestaoOf/producao.html', {'error': "Erro ao conectar ao banco de dados."})


    

    try:
        # Inicializar filtros
        marca = request.GET.get('marca', '')
        modelo = request.GET.get('modelo', '')
        tamanho = request.GET.get('tamanho', '')
        data_inicio = request.GET.get('data_inicio', '')
        data_fim = request.GET.get('data_fim', '')
        nave = request.GET.get('nave', '').strip()
        of_mae = request.GET.get('of_mae', '')

        logging.info(f"Filtros recebidos: marca={marca}, modelo={modelo}, tamanho={tamanho}, data_inicio={data_inicio}, data_fim={data_fim}, nave={nave}, of_mae={of_mae}")

        # Obter opções para filtros
        cursor.execute("SELECT DISTINCT nave FROM u_prod_work_center_alb WHERE nave IS NOT NULL ORDER BY nave")
        naves = [row[0] for row in cursor.fetchall()]
        logging.info(f"Naves obtidas: {naves}")

        cursor.execute("SELECT DISTINCT usr1 FROM st ORDER BY usr1")
        marcas = [row[0] for row in cursor.fetchall()]
        logging.info(f"Marcas obtidas: {marcas}")

        cursor.execute("SELECT DISTINCT ofparent FROM u_fo_alb WHERE ofparent IS NOT NULL ORDER BY ofparent")
        of_mae_list = [row[0] for row in cursor.fetchall()]
        logging.info(f"OFs Mãe obtidas: {of_mae_list}")

        modelos = []
        if marca:
            cursor.execute("SELECT DISTINCT usr2 FROM st WHERE usr1 = ? ORDER BY usr2", (marca,))
            modelos = [row[0] for row in cursor.fetchall()]
            logging.info(f"Modelos obtidos para a marca {marca}: {modelos}")

        tamanhos = []
        if modelo:
            cursor.execute("SELECT DISTINCT u_tamanho FROM st WHERE usr2 = ? ORDER BY u_tamanho", (modelo,))
            tamanhos = [row[0] for row in cursor.fetchall()]
            logging.info(f"Tamanhos obtidos para o modelo {modelo}: {tamanhos}")
    
    except Exception as e:
        logging.error(f"Erro ao obter opções para filtros: {e}")
        return render(request, 'gestaoOf/producao.html', {'error': "Erro ao obter opções para filtros."})


    data = None
    page_obj = None  # Inicializar page_obj como None

    if marca or modelo or tamanho or data_inicio or data_fim or nave:
        # Criação da tabela temporária com a hierarquia
        logging.info("Criando tabela temporária com a hierarquia")
        
        cursor.execute("DROP TABLE IF EXISTS u_temp_teste_alb")

        cursor.execute("""
            ;WITH ParentChildCTE AS (
                SELECT id_parent as id, parent, 1 as level, id_parent as aux
                FROM u_fo_gama_alb
                WHERE parent = 0
                UNION ALL
                SELECT T1.ID_parent, T1.parent, level + 1 as level, aux
                FROM u_fo_gama_alb T1
                INNER JOIN ParentChildCTE T ON T.ID = T1.parent
                WHERE T1.parent IS NOT NULL
            )
            SELECT obrano_fo
            INTO u_temp_teste_alb
            FROM ParentChildCTE
            LEFT JOIN u_fo_alb fo ON fo.id_parent = ParentChildCTE.id
        """)

        logging.info("Tabela temporária criada com sucesso")
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
            INNER JOIN 
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
        
        logging.info("Montando query principal com filtros")

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
            
        logging.info("Adicionando filtros à query")
        

        # Adicionar ordenação baseada na tabela temporária
        query += """
            ORDER BY 
                (SELECT TOP 1 ROW_NUMBER() OVER (ORDER BY (SELECT NULL))
                 FROM u_temp_teste_alb
                 WHERE u_temp_teste_alb.obrano_fo = u_fo_alb.obrano_fo)
        """
        
        logging.info("Adicionando ordenação baseada na tabela temporária")

        # Executar a query principal
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        logging.info("Query principal executada com sucesso")

        # Processar os dados (como no código original)

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
                
                logging.info(f"Adicionando OF Mãe {ofmae} ao dicionário de dados")
                
                # Calcular a porcentagem do processo
            pedido = row['Pedido'] if row['Pedido'] is not None else 0  # Verificar se 'Pedido' é None
            produzida = row['qtt_produzida'] if row['qtt_produzida'] is not None else 0
            rejeitada = row['qtt_rejeitada'] if row['qtt_rejeitada'] is not None else 0
            
            logging.info(f"Calculando a porcentagem do processo para a SubOF {row['SubOF']}")

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
            
            logging.info(f"Adicionando SubOF {row['SubOF']} ao dicionário de dados")
            
        data_list = [{'OFMae': key, **value} for key, value in data.items()]
        
        logging.info("Dados organizados com sucesso")

        # Paginação


        # Excluir tabela temporária
        cursor.execute("DROP TABLE IF EXISTS u_temp_teste_alb")
        
        logging.info("Tabela temporária excluída com sucesso")

    conn.close()
    
    logging.info("Conexão ao banco de dados encerrada")
    
    #data atual
    data_inicio= time.strftime('%Y-%m-%d')
    #data atual + 1 semana
    data_fim = time.strftime('%Y-%m-%d', time.localtime(time.time() + 604800))

    return render(request, 'gestaoOf/producao.html', {
        'marcas': marcas,
        'modelos': modelos,
        'tamanhos': tamanhos,
        'naves': naves,
        'of_mae_list': of_mae_list,
        'data': data,  # page_obj pode ser None ou uma página de dados
        'data_fim': data_fim,
        'data_inicio': data_inicio,
        'filtros': {'marca': marca, 'modelo': modelo, 'tamanho': tamanho, 'data_inicio': data_inicio, 'data_fim': data_fim, 'nave': nave, 'of_mae': of_mae},
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