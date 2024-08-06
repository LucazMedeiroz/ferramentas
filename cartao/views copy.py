import base64
from django.shortcuts import render
from django.http import HttpResponse
from cartao.utils import dados_funcinario
from reportlab.pdfgen import canvas
import win32print
import win32api
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Definindo o tamanho do cartão em polegadas
credit_card_size = (2.17 * inch, 3.35 * inch)  # Largura x Altura

import logging

# Configurar o logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

credit_card_size = (2.17 * inch, 3.35 * inch)  # Largura x Altura
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import cm
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
import io

def create_card(template_path, output_path, nome_usuario, id_usuario, descricao, data_admissao, foto_path, qrcode_base64):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(5.5 * cm, 8.5 * cm))
    
    # Carregar e desenhar a foto do funcionário
    if foto_path:
        foto = ImageReader(foto_path)
        can.drawImage(foto, 1.5 * cm, 5 * cm, 2.5 * cm, 2.5 * cm)  # Ajuste a posição e o tamanho conforme necessário

    # Adicionar o nome do usuário
    can.setFont("Helvetica", 12)
    can.drawString(1 * cm, 4.5 * cm, nome_usuario)
    
    # Adicionar a descrição
    can.setFont("Helvetica", 8)
    can.drawString(1 * cm, 3.5 * cm, descricao)
    
    # Adicionar a data de admissão
    can.setFont("Helvetica", 8)
    can.drawString(1 * cm, 3.2 * cm, f"Data de admissão: {data_admissao}")
    
    # Adicionar o número do usuário
    can.setFont("Helvetica", 8)
    can.drawString(1 * cm, 2.9 * cm, f"Número: {id_usuario}")
    
    # Adicionar o QR code na parte de trás
    qr_code_img = ImageReader(io.BytesIO(base64.b64decode(qrcode_base64)))
    can.drawImage(qr_code_img, 2 * cm, 1 * cm, 1.5 * cm, 1.5 * cm)  # Ajuste a posição e o tamanho conforme necessário
    
    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)

    # Read your existing PDF
    existing_pdf = PdfFileReader(open(template_path, "rb"))
    output = PdfFileWriter()

    # Add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)

    # Finally, write "output" to a real file
    outputStream = open(output_path, "wb")
    output.write(outputStream)
    outputStream.close()




def get_printers():
    printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]
    logger.debug(f"Impressoras encontradas: {printers}")
    return printers



import logging
logger = logging.getLogger(__name__)

import win32print
import win32api
import os
import win32print
import win32ui
from PIL import Image

import win32print
import os
import win32print
import win32ui
from PyPDF2 import PdfFileReader, PdfFileWriter

def get_printers():
    return [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]

def print_card(printer_name, filename):
    if not os.path.exists(filename):
        logger.error(f"O arquivo {filename} não foi encontrado.")
        raise FileNotFoundError(f"O arquivo {filename} não foi encontrado.")
    
    try:
        printers = get_printers()
        if printer_name not in printers:
            logger.error(f"A impressora '{printer_name}' não está instalada no sistema.")
            raise ValueError(f"A impressora '{printer_name}' não está instalada no sistema.")

        hprinter = win32print.OpenPrinter(printer_name)
        try:
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(printer_name)
            hdc.StartDoc("Cartao")
            hdc.StartPage()

            # Open PDF file
            with open(filename, 'rb') as file:
                pdf_reader = PdfFileReader(file)
                for page_num in range(pdf_reader.numPages):
                    page = pdf_reader.getPage(page_num)
                    temp_pdf_filename = f'temp_page_{page_num}.pdf'

                    # Save single page to temporary file
                    with open(temp_pdf_filename, 'wb') as temp_pdf_file:
                        pdf_writer = PdfFileWriter()
                        pdf_writer.addPage(page)
                        pdf_writer.write(temp_pdf_file)

                    # Print single page
                    win32api.ShellExecute(0, "print", temp_pdf_filename, f'/d:"{printer_name}"', ".", 0)

                    # Remove temporary file
                    os.remove(temp_pdf_filename)

            hdc.EndPage()
            hdc.EndDoc()
            hdc.DeleteDC()
        finally:
            win32print.ClosePrinter(hprinter)
        
        logger.info(f"O arquivo {filename} foi enviado para a impressora {printer_name}.")
    except Exception as e:
        logger.error(f"Ocorreu um erro ao tentar imprimir: {e}")
        raise


from django.shortcuts import render
from django.http import HttpResponse
import os
from .utils import dados_funcinario, create_card, get_printers, print_card
import base64
from PyPDF2 import PdfFileReader, PdfFileWriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def cartao(request):
    printers = get_printers()
    
    if request.method == 'POST':
        numero = request.POST.get('numero')
        printer_name = request.POST.get('printer_name')
        
        dados = dados_funcinario(numero)

        if dados:
            nome_usuario = dados[0].get('nome', 'Desconhecido')
            id_usuario = dados[0].get('Numero', 'Desconhecido')
            descricao = dados[0].get('Descricao', 'Desconhecida')
            data_admissao = dados[0].get('dataadmissao', 'Desconhecida')
            foto_base64 = dados[0].get('fotografia')
            qrcode_base64 = dados[0].get('qrcode')

            # Caminhos para os arquivos
            template_path = os.path.abspath("layout.pdf")
            output_path = os.path.abspath("cartao.pdf")
            foto_path = None

            if foto_base64:
                foto_path = os.path.abspath("foto.jpg")
                with open(foto_path, "wb") as foto_file:
                    foto_file.write(base64.b64decode(foto_base64))

            # Criar o cartão
            create_card(template_path, output_path, nome_usuario, id_usuario, descricao, data_admissao, foto_path, qrcode_base64)
            
            # Remover a imagem temporária se foi criada
            if foto_path:
                os.remove(foto_path)
            
            # Ler o PDF gerado e convertê-lo para uma imagem base64
            preview_base64 = None
            with open(output_path, "rb") as pdf_file:
                pdf_reader = PdfFileReader(pdf_file)
                page = pdf_reader.getPage(0)
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=(5.5 * cm, 8.5 * cm))
                can.drawImage(page, 0, 0, 5.5 * cm, 8.5 * cm)
                can.save()
                packet.seek(0)
                preview_base64 = base64.b64encode(packet.getvalue()).decode('utf-8')

            context = {
                'dados': dados,
                'numero': numero,
                'printers': printers,
                'preview': preview_base64
            }

            if 'print' in request.POST:
                print_card(printer_name, output_path)
                os.remove(output_path)

            return render(request, 'cartao/cartao.html', context)

    return render(request, 'cartao/cartao.html', {'printers': printers})
