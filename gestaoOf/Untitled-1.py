
from django.shortcuts import render
from django.core.paginator import Paginator
import pyodbc


def producao_view(request):
    # Conectar ao SQL Server
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=192.168.120.9;'
        'DATABASE=PHCTRI;'
        'UID=estagio;'
        'PWD=3stAg10..;'
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
    page_obj = None  # Inicializar page_obj como None

    if marca or modelo or tamanho or data_inicio or data_fim or nave:
        # Criação da tabela temporária com a hierarquia
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

        # Adicionar ordenação baseada na tabela temporária
        query += """
            ORDER BY 
                (SELECT TOP 1 ROW_NUMBER() OVER (ORDER BY (SELECT NULL))
                 FROM u_temp_teste_alb
                 WHERE u_temp_teste_alb.obrano_fo = u_fo_alb.obrano_fo)
        """

        # Executar a query principal
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Processar os dados (como no código original)

        # Excluir tabela temporária
        cursor.execute("DROP TABLE IF EXISTS u_temp_teste_alb")

    conn.close()

    return render(request, 'gestaoOf/producao.html', {
        'marcas': marcas,
        'modelos': modelos,
        'tamanhos': tamanhos,
        'naves': naves,
        'of_mae_list': of_mae_list,
        'data': data,  # page_obj pode ser None ou uma página de dados
        'filtros': {'marca': marca, 'modelo': modelo, 'tamanho': tamanho, 'data_inicio': data_inicio, 'data_fim': data_fim, 'nave': nave, 'of_mae': of_mae},
    })
