


import pyodbc



def queryValidador(ref):
    


    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    query = f"""
                select
                    v.*, o.imp, o.da_entrada, o.id_op, o.id, o.parent
                from
                    u_prod_gama_versao_alb v
                INNER JOIN
                    u_prod_gama_operations_alb o ON v.id = o.id_version
                where
                    v.active = 1
                    and
                    v.type != 4
                    and
                    v.main_ref = '{ref}'
                    
                order by v.id desc
                """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    dados = []
    for row in rows:
        dados.append(row)
    return dados




def queryValidadorSRef():
    


    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    query = f"""
                select
                    v.*, o.imp, o.da_entrada, o.id_op, o.id, o.parent
                from
                    u_prod_gama_versao_alb v
                INNER JOIN
                    u_prod_gama_operations_alb o ON v.id = o.id_version
                where
                    v.active = 1
                    and
                    v.type != 4
                                        
                order by v.id desc
                """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    dados = []
    for row in rows:
        dados.append(row)
    return dados


#validar of
def queryValidadorOF(of):
    


    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    query = f"""
        select 
            f.play, f.stop, f.gerar_consumo, f.ref, f.id, s.id, s.id_fo, s.operation_name, s.operator_id, s.initial, s.final
        from 
            u_fo_alb f
        INNER JOIN
            u_shopfloor_alb s on f.id = s.id_fo
        where
            f.obrano_fo = '{of}'
        """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    dados = []
    for row in rows:
        dados.append(row)
    return dados


def updateOf(ref):
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    query = f"""
        update u_fo_alb set play = 0, stop = 0  where obrano_fo = '{ref}'
        """
    cursor.execute(query)
    conn.commit()
    return True










