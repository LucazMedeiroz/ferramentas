


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
   SELECT 
    SmartTime.dbo.Funcionarios.nome, 
    SmartTime.dbo.Funcionarios.Numero, 
    u_operators_alb.email, 
    qrcode, 
    SmartTime.dbo.Funcionarios.Fotografia, 
    SmartTime.dbo.Departamentos.Descricao, 
    CONVERT(VARCHAR(10), SmartTime.dbo.Funcionarios.DataAdmissao, 120) AS dataadmissao
FROM 
    SmartTime.dbo.Funcionarios 
LEFT JOIN 
    dbo.u_operators_alb ON u_operators_alb.numphc = SmartTime.dbo.Funcionarios.Numero
LEFT JOIN 
    dbo.pe ON SmartTime.dbo.Funcionarios.Numero = dbo.pe.no
LEFT JOIN 
    SmartTime.dbo.Departamentos ON SmartTime.dbo.Departamentos.IDDepartamento = SmartTime.dbo.Funcionarios.IDDepartamento
WHERE 
    SmartTime.dbo.Funcionarios.Activo = 1
    AND SmartTime.dbo.Funcionarios.Numero = {numero}
ORDER BY 
    SmartTime.dbo.Funcionarios.Numero


                """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    dados = []

    for row in rows:
        # Converting the Fotografia to base64
        fotografia_base64 = base64.b64encode(row.Fotografia).decode('utf-8') if row.Fotografia else None

        # Generating the QR code


        qr_code_img = qrcode.make(row.qrcode)
        buffer = BytesIO()
        qr_code_img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Inicializa o dicionário com dados comuns
        dado = {
            'nome': row.nome,
            'Numero': row.Numero,
            'email': row.email,
            'fotografia': fotografia_base64,
            'Descricao': row.Descricao,
            'dataadmissao': row.dataadmissao
        }

        # Adiciona o QR code somente se existir
        if row.qrcode:
            qr_code_img = qrcode.make(row.qrcode)
            buffer = BytesIO()
            qr_code_img.save(buffer, format="PNG")
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            dado['qrcode'] = qr_code_base64

        dados.append(dado)

    
    return dados


