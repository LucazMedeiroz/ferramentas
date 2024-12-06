


import pyodbc
from turtle import pd
import pyodbc
import base64
import qrcode
from io import BytesIO



def dados_funcinario(numero):
    


    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=192.168.120.9;DATABASE=PHCTRI;UID=estagio;PWD=3stAg10..')
    cursor = conn.cursor()
    query = f"""
select  u_fo_alb.data_entrega,u_prod_work_center_alb.nave,
u_fo_alb.ofparent,u_fo_alb.obrano_fo,u_fo_alb.qtt_real,u_fo_alb.qtt,u_fo_alb.qtt_produzida,
u_shopfloor_alb.ct_design,
MÊS=MONTH(u_shopfloor_alb.final),
SEMANA=DATEPART(week, u_shopfloor_alb.final),
 
DIA_Diario=DAY(u_shopfloor_alb.final),
PRODUCAO=sum(u_shopfloor_alb.qtt),
u_sections_alb.name,
 
MODELO=st.usr2,COMPONENTE=st.lang4,
u_shopfloor_alb.id
 
from u_shopfloor_alb 
inner join u_fo_alb on u_fo_alb.id = u_shopfloor_alb.id_fo
 
inner join st on u_fo_alb.ref =  st.ref
inner join u_prod_work_center_alb on  u_prod_work_center_alb.design = u_shopfloor_alb.ct_design
inner join u_sections_alb on u_sections_alb.id=u_prod_work_center_alb.id_section
 
where u_shopfloor_alb.rework <>1 and u_prod_work_center_alb.nave=1 and u_shopfloor_alb.rework=0  and datediff ( DAY , CAST (GETDATE() as date), final) > -60 and u_fo_alb.status in (2,4) and u_fo_alb.conversao =0
 
group by
 
u_fo_alb.data_entrega,u_prod_work_center_alb.nave,
u_fo_alb.ofparent,u_fo_alb.obrano_fo,u_fo_alb.qtt_real,u_fo_alb.qtt,u_fo_alb.qtt_produzida,
u_shopfloor_alb.ct_design,
MONTH(u_shopfloor_alb.final),
DATEPART(week, u_shopfloor_alb.final),
DAY(u_shopfloor_alb.final),
DAY(u_shopfloor_alb.final),
u_sections_alb.name,
st.usr2,st.lang4,
u_shopfloor_alb.id,
u_shopfloor_alb.final
 
order by final,u_shopfloor_alb.ct_design asc
 

                """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    dados = []

    for row in rows:

        # Inicializa o dicionário com dados comuns
        dado = {
            "id": row.id,
            "data_entrega": row.data_entrega,
            "nave": row.nave,
            "ofparent": row.ofparent,
            "obrano_fo": row.obrano_fo,
            "qtt_real": row.qtt_real,
            "qtt": row.qtt,
            "qtt_produzida": row.qtt_produzida,
            "ct_design": row.ct_design,
            "month": row.month,
            "week": row.week,
            "day": row.day,
            "producao": row.producao,
            "name": row.name,
            "usr2": row.usr2,
            "lang4": row.lang4,
            "final": row.final,
            "status": row.status
            
            }
        

        

        # Adiciona o QR code somente se existir


        dados.append(dado)

    
    return dados




