from django.shortcuts import render
import pyodbc

def processa_dados(results):
    dados_processados = []

    # Dicionário para agrupar dados pela OF mãe
    of_mae_dict = {}

    for row in results:
        marca = row[0]
        modelo = row[1]
        tamanho = row[2]
        qtt_real = row[3]
        of_parent = row[4]
        sequencial = row[5]
        data_entrega = row[6]
        nave = row[7]
        obrano_fo = row[8]
        componente = row[9]
        name = row[10]
        design = row[11]
        ref = row[12]
        qtt_real_2 = row[13]
        qtt_produzida = row[14]
        qtt_rejeitada = row[15]

        # Agrupa por OF mãe
        if obrano_fo not in of_mae_dict:
            of_mae_dict[obrano_fo] = {
                'marca': marca,
                'modelo': modelo,
                'tamanho': tamanho,
                'of_mae': obrano_fo,
                'componentes': []
            }

        # Adiciona o componente e sub-OFs à OF mãe
        of_mae_dict[obrano_fo]['componentes'].append({
            'componente': componente,
            'of_parent': of_parent,
            'sequencial': sequencial,
            'data_entrega': data_entrega,
            'nave': nave,
            'qtt_real': qtt_real,
            'qtt_produzida': qtt_produzida,
            'qtt_rejeitada': qtt_rejeitada,
            'design': design,
            'ref': ref,
            'name': name,
        })

    # Converte o dicionário para uma lista para uso no template
    dados_processados = list(of_mae_dict.values())
    return dados_processados

from django.shortcuts import render
import pyodbc

def consulta_producao1(request):
    # Inicializa as variáveis de filtro com valores padrão (vazios)
    filtro_marca = ''
    filtro_modelo = ''
    filtro_tamanho = ''
    data_inicio = ''
    data_fim = ''
    
    # Conectar ao SQL Server com pyodbc
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()

    # Query para obter opções de filtro para marcas, modelos e tamanhos
    query_opcoes = """
    SELECT DISTINCT 
        parent_st.usr1 AS marca,
        parent_st.usr2 AS modelo,
        parent_st.u_tamanho AS tamanho
    FROM 
        u_shopfloor_alb
    INNER JOIN 
        u_fo_alb ON u_fo_alb.id = u_shopfloor_alb.id_fo
    INNER JOIN 
        st ON u_fo_alb.ref = st.ref
    INNER JOIN 
        u_prod_work_center_alb ON u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
    INNER JOIN 
        u_sections_alb ON u_sections_alb.id = u_prod_work_center_alb.id_section
    LEFT JOIN 
        u_fo_alb parent_fo ON parent_fo.id = u_fo_alb.ofparent
    LEFT JOIN 
        st parent_st ON parent_fo.ref = parent_st.ref
    WHERE 
        u_shopfloor_alb.rework <> 1 
        AND u_prod_work_center_alb.nave = 1 
        AND u_shopfloor_alb.rework = 0  
        AND DATEDIFF(DAY, CAST(GETDATE() AS DATE), u_shopfloor_alb.final) > -60 
        AND u_fo_alb.status IN (2, 4) 
        AND u_fo_alb.conversao = 0
    """

    cursor.execute(query_opcoes)
    opcoes = cursor.fetchall()

    # Processar as opções em listas distintas para cada filtro
    marcas = list(set([row[0] for row in opcoes if row[0] is not None]))
    modelos = list(set([row[1] for row in opcoes if row[1] is not None]))
    tamanhos = list(set([row[2] for row in opcoes if row[2] is not None]))

    # Verifica se o formulário foi submetido
    if request.method == "POST":
        # Obtém os valores filtrados do formulário
        filtro_marca = request.POST.get('marca', '')
        filtro_modelo = request.POST.get('modelo', '')
        filtro_tamanho = request.POST.get('tamanho', '')
        data_inicio = request.POST.get('data_inicio', '')
        data_fim = request.POST.get('data_fim', '')

        # Query para buscar os dados filtrados
        query_dados = """
        SELECT 
            parent_st.usr1 AS marca,
            parent_st.usr2 AS modelo,
            parent_st.u_tamanho AS tamanho,
            u_fo_alb.qtt_real, 
            u_fo_alb.ofparent,
            u_fo_alb.sequencial,
            u_fo_alb.data_entrega,
            u_prod_work_center_alb.nave,
            u_fo_alb.obrano_fo AS of_mae,
            st.lang4 AS componente,
            u_sections_alb.name AS name_section,
            st.design,
            u_fo_alb.ref,
            u_fo_alb.qtt_real,
            u_fo_alb.qtt_produzida,
            u_fo_alb.qtt_rejeitada
        FROM 
            u_shopfloor_alb
        INNER JOIN 
            u_fo_alb ON u_fo_alb.id = u_shopfloor_alb.id_fo
        INNER JOIN 
            st ON u_fo_alb.ref = st.ref
        INNER JOIN 
            u_prod_work_center_alb ON u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
        INNER JOIN 
            u_sections_alb ON u_sections_alb.id = u_prod_work_center_alb.id_section
        LEFT JOIN 
            u_fo_alb parent_fo ON parent_fo.id = u_fo_alb.ofparent
        LEFT JOIN 
            st parent_st ON parent_fo.ref = parent_st.ref
        WHERE 
            u_shopfloor_alb.rework <> 1 
            AND u_prod_work_center_alb.nave = 1 
            AND u_shopfloor_alb.rework = 0  
            AND DATEDIFF(DAY, CAST(GETDATE() AS DATE), u_shopfloor_alb.final) > -60 
            AND u_fo_alb.status IN (2, 4) 
            AND u_fo_alb.conversao = 0
        """
        
        # Adicionar filtros à query de dados
        if filtro_marca:
            query_dados += f" AND parent_st.usr1 LIKE '%{filtro_marca}%'"
        if filtro_modelo:
            query_dados += f" AND parent_st.usr2 LIKE '%{filtro_modelo}%'"
        if filtro_tamanho:
            query_dados += f" AND parent_st.u_tamanho LIKE '%{filtro_tamanho}%'"
        if data_inicio:
            query_dados += f" AND u_fo_alb.data_entrega >= '{data_inicio}'"
        if data_fim:
            query_dados += f" AND u_fo_alb.data_entrega <= '{data_fim}'"

        cursor.execute(query_dados)
        dados = cursor.fetchall()
    else:
        # Se o método não for POST, não aplica filtros e traz todos os dados
        query_dados = """
        SELECT 
            parent_st.usr1 AS marca,
            parent_st.usr2 AS modelo,
            parent_st.u_tamanho AS tamanho,
            u_fo_alb.qtt_real, 
            u_fo_alb.ofparent,
            u_fo_alb.sequencial,
            u_fo_alb.data_entrega,
            u_prod_work_center_alb.nave,
            u_fo_alb.obrano_fo AS of_mae,
            st.lang4 AS componente,
            u_sections_alb.name AS name_subof,
            st.design,
            u_fo_alb.ref,
            u_fo_alb.qtt_real,
            u_fo_alb.qtt_produzida,
            u_fo_alb.qtt_rejeitada
        FROM 
            u_shopfloor_alb
        INNER JOIN 
            u_fo_alb ON u_fo_alb.id = u_shopfloor_alb.id_fo
        INNER JOIN 
            st ON u_fo_alb.ref = st.ref
        INNER JOIN 
            u_prod_work_center_alb ON u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
        INNER JOIN 
            u_sections_alb ON u_sections_alb.id = u_prod_work_center_alb.id_section
        LEFT JOIN 
            u_fo_alb parent_fo ON parent_fo.id = u_fo_alb.ofparent
        LEFT JOIN 
            st parent_st ON parent_fo.ref = parent_st.ref
        WHERE 
            u_shopfloor_alb.rework <> 1 
            AND u_prod_work_center_alb.nave = 1 
            AND u_shopfloor_alb.rework = 0  
            AND DATEDIFF(DAY, CAST(GETDATE() AS DATE), u_shopfloor_alb.final) > -60 
            AND u_fo_alb.status IN (2, 4) 
            AND u_fo_alb.conversao = 0
        """
        cursor.execute(query_dados)
        dados = cursor.fetchall()

    # Passar as opções e dados para o template
    return render(request, 'gestaoOf/producao.html', {
        'dados': dados,
        'marcas': marcas,
        'modelos': modelos,
        'tamanhos': tamanhos,
        'filtro_marca': filtro_marca,
        'filtro_modelo': filtro_modelo,
        'filtro_tamanho': filtro_tamanho,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    })
    
    ##
    

def consulta_producao(request):
    # Inicializa as variáveis de filtro com valores padrão (vazios)
    filtro_marca = ''
    filtro_modelo = ''
    filtro_tamanho = ''
    data_inicio = ''
    data_fim = ''
    
    # Conectar ao SQL Server com pyodbc
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()

    # Query para obter opções de filtro para marcas, modelos e tamanhos
    query_opcoes = """
    SELECT DISTINCT 
        parent_st.usr1 AS marca,
        parent_st.usr2 AS modelo,
        parent_st.u_tamanho AS tamanho
    FROM 
        u_shopfloor_alb
    INNER JOIN 
        u_fo_alb ON u_fo_alb.id = u_shopfloor_alb.id_fo
    INNER JOIN 
        st ON u_fo_alb.ref = st.ref
    INNER JOIN 
        u_prod_work_center_alb ON u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
    INNER JOIN 
        u_sections_alb ON u_sections_alb.id = u_prod_work_center_alb.id_section
    LEFT JOIN 
        u_fo_alb parent_fo ON parent_fo.id = u_fo_alb.ofparent
    LEFT JOIN 
        st parent_st ON parent_fo.ref = parent_st.ref
    WHERE 
        u_shopfloor_alb.rework <> 1 
        AND u_prod_work_center_alb.nave = 1 
        AND u_shopfloor_alb.rework = 0  
        AND DATEDIFF(DAY, CAST(GETDATE() AS DATE), u_shopfloor_alb.final) > -60 
        AND u_fo_alb.status IN (2, 4) 
        AND u_fo_alb.conversao = 0
    """

    cursor.execute(query_opcoes)
    opcoes = cursor.fetchall()

    # Processar as opções em listas distintas para cada filtro
    marcas = list(set([row[0] for row in opcoes if row[0] is not None]))
    modelos = list(set([row[1] for row in opcoes if row[1] is not None]))
    tamanhos = list(set([row[2] for row in opcoes if row[2] is not None]))

    # Verifica se o formulário foi submetido
    if request.method == "POST":
        # Obtém os valores filtrados do formulário
        filtro_marca = request.POST.get('marca', '')
        filtro_modelo = request.POST.get('modelo', '')
        filtro_tamanho = request.POST.get('tamanho', '')
        data_inicio = request.POST.get('data_inicio', '')
        data_fim = request.POST.get('data_fim', '')

        # Query para buscar os dados filtrados
        query_dados = """
        SELECT 
            parent_st.usr1 AS marca,
            parent_st.usr2 AS modelo,
            parent_st.u_tamanho AS tamanho,
            u_fo_alb.qtt_real, 
            u_fo_alb.ofparent as ofmae,
            u_fo_alb.sequencial,
            u_fo_alb.data_entrega,
            u_prod_work_center_alb.nave,
            u_fo_alb.obrano_fo AS subof,
            st.lang4 AS componente,
            u_sections_alb.name AS seccao,
            st.design,
            u_fo_alb.ref,
            u_fo_alb.qtt_real,
            u_fo_alb.qtt_produzida,
            u_fo_alb.qtt_rejeitada
        FROM 
            u_shopfloor_alb
        INNER JOIN 
            u_fo_alb ON u_fo_alb.id = u_shopfloor_alb.id_fo
        INNER JOIN 
            st ON u_fo_alb.ref = st.ref
        INNER JOIN 
            u_prod_work_center_alb ON u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
        INNER JOIN 
            u_sections_alb ON u_sections_alb.id = u_prod_work_center_alb.id_section
        LEFT JOIN 
            u_fo_alb parent_fo ON parent_fo.id = u_fo_alb.ofparent
        LEFT JOIN 
            st parent_st ON parent_fo.ref = parent_st.ref
        WHERE 
            u_shopfloor_alb.rework <> 1 
            AND u_prod_work_center_alb.nave = 1 
            AND u_shopfloor_alb.rework = 0  
            AND DATEDIFF(DAY, CAST(GETDATE() AS DATE), u_shopfloor_alb.final) > -60 
            AND u_fo_alb.status IN (2, 4) 
            AND u_fo_alb.conversao = 0
        """
        
        # Adicionar filtros à query de dados
        if filtro_marca:
            query_dados += f" AND parent_st.usr1 LIKE '%{filtro_marca}%'"
        if filtro_modelo:
            query_dados += f" AND parent_st.usr2 LIKE '%{filtro_modelo}%'"
        if filtro_tamanho:
            query_dados += f" AND parent_st.u_tamanho LIKE '%{filtro_tamanho}%'"
        if data_inicio:
            query_dados += f" AND u_fo_alb.data_entrega >= '{data_inicio}'"
        if data_fim:
            query_dados += f" AND u_fo_alb.data_entrega <= '{data_fim}'"

        cursor.execute(query_dados)
        dados = cursor.fetchall()
    else:
        # Se o método não for POST, não aplica filtros e traz todos os dados
        query_dados = """
        SELECT 
            parent_st.usr1 AS marca,
            parent_st.usr2 AS modelo,
            parent_st.u_tamanho AS tamanho,
            u_fo_alb.qtt_real, 
            u_fo_alb.ofparent as ofmae,
            u_fo_alb.sequencial,
            u_fo_alb.data_entrega,
            u_prod_work_center_alb.nave,
            u_fo_alb.obrano_fo AS subof,
            st.lang4 AS componente,
            u_sections_alb.name AS seccao,
            st.design,
            u_fo_alb.ref,
            u_fo_alb.qtt_real,
            u_fo_alb.qtt_produzida,
            u_fo_alb.qtt_rejeitada
        FROM 
            u_shopfloor_alb
        INNER JOIN 
            u_fo_alb ON u_fo_alb.id = u_shopfloor_alb.id_fo
        INNER JOIN 
            st ON u_fo_alb.ref = st.ref
        INNER JOIN 
            u_prod_work_center_alb ON u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
        INNER JOIN 
            u_sections_alb ON u_sections_alb.id = u_prod_work_center_alb.id_section
        LEFT JOIN 
            u_fo_alb parent_fo ON parent_fo.id = u_fo_alb.ofparent
        LEFT JOIN 
            st parent_st ON parent_fo.ref = parent_st.ref
        WHERE 
            u_shopfloor_alb.rework <> 1 
            AND u_prod_work_center_alb.nave = 1 
            AND u_shopfloor_alb.rework = 0  
            AND DATEDIFF(DAY, CAST(GETDATE() AS DATE), u_shopfloor_alb.final) > -60 
            AND u_fo_alb.status IN (2, 4) 
            AND u_fo_alb.conversao = 0
        """
        cursor.execute(query_dados)
        dados = cursor.fetchall()

    # Processar os dados para agrupamento
    dados_processados = processa_dados(dados)

    # Passar as opções e dados para o template
    return render(request, 'gestaoOf/producao.html', {
        'dados': dados_processados,
        'marcas': marcas,
        'modelos': modelos,
        'tamanhos': tamanhos,
        'filtro_marca': filtro_marca,
        'filtro_modelo': filtro_modelo,
        'filtro_tamanho': filtro_tamanho,
        'data_inicio': data_inicio,
        'data_fim': data_fim
    })

