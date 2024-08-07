from django.shortcuts import render
from django.http import Http404, HttpResponse
from cartao.utils import dados_funcinario
from reportlab.pdfgen import canvas
import win32print
import win32api
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

from ferramentas import settings

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
from reportlab.lib.pagesizes import mm
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
import io
import base64
from reportlab.lib.colors import white


# Definição do tamanho do cartão em milímetros
CARD_WIDTH, CARD_HEIGHT = 55 * mm, 85 * mm


# Definição do tamanho do cartão em milímetros
CARD_WIDTH, CARD_HEIGHT = 55 * mm, 85 * mm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import white, black
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics

import io
import base64
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfbase.ttfonts import TTFont
#importar otf


# Definição do tamanho do cartão em milímetros


from django.contrib.auth.decorators import user_passes_test

def user_in_groups(groups):
    def check_user(user):
        return user.is_authenticated and any(group.name in groups for group in user.groups.all())
    return user_passes_test(check_user)



def wrap_text(text, max_length):
    """Wrap text into multiple lines with a maximum length."""
    lines = []
    while len(text) > max_length:
        # Find the last space within max_length
        split_index = text.rfind(' ', 0, max_length)
        if split_index == -1:
            split_index = max_length
        lines.append(text[:split_index].strip())
        text = text[split_index:].strip()
    if text:
        lines.append(text)
    return lines


CARD_WIDTH, CARD_HEIGHT = 54 * mm, 85.7 * mm


def create_card(template_file, output_path, nome_usuario, id_usuario, descricao, data_admissao, foto_path, qrcode_base64):
    print('create_card')

        # Caminho absoluto para a pasta de fontes
    base_dir = os.path.dirname(os.path.abspath(__file__))
    font_dir = os.path.join(base_dir, 'fonts')
    
        
    # Registrar as fontes Scandia
    pdfmetrics.registerFont(TTFont('Scandia_Bold', os.path.join(font_dir, 'fonnts.com-Scandia_Bold.ttf')))
    pdfmetrics.registerFont(TTFont('Scandia', os.path.join(font_dir, 'fonnts.com-Scandia.ttf')))


    






    
    
    


    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=(CARD_WIDTH, CARD_HEIGHT))

    # Carregar e desenhar a foto do funcionário
    # Carregar e desenhar a foto do funcionário com tamanho aumentado e posição ajustada
    # Carregar e desenhar a foto do funcionário com tamanho aumentado e posição ajustada
    if foto_path:
        foto = ImageReader(foto_path)
        foto_width = 30 * mm
        foto_height = 30 * mm
        # Calcular a posição horizontal para centralizar a foto
        x_position = (CARD_WIDTH - foto_width) / 2 + 0.16 * mm
        y_position = CARD_HEIGHT - 4.7 * mm - foto_height
        can.drawImage(foto, x_position, y_position, foto_width, foto_height)

    # Adicionar o nome do usuário
    can.setFont("Scandia", 11.5)
    can.setFillColor(black)  # Cor preta para o nome

    # Quebrar o nome em várias linhas se necessário
    nome_usuario_linhas = []
    nome_usuario_atual = ""
    
    for palavra in nome_usuario.split():
        if len(nome_usuario_atual + palavra) <= 17:
            nome_usuario_atual += palavra + " "
        else:
            nome_usuario_linhas.append(nome_usuario_atual.strip())
            nome_usuario_atual = palavra + " "
    
    if nome_usuario_atual:
        nome_usuario_linhas.append(nome_usuario_atual.strip())

    y_position = 43.5 * mm
    for linha in nome_usuario_linhas:
        text_width = can.stringWidth(linha, "Scandia", 11.5)
        can.setFillColor(black)  # Cor preta para o nome

        x_position = (CARD_WIDTH - text_width) / 2  # Centraliza o texto horizontalmente
        can.drawString(x_position, y_position, linha)
        y_position -= 12  # Ajuste o espaçamento entre linhas conforme necessário



    if descricao:
        # Adicionar a descrição, com quebra de linha após 12 caracteres
        can.setFont("Scandia", 5.5)
        can.setFillColor(white)  # Cor branca para a descrição

        descricao_linhas = wrap_text(descricao, 12)  # Quebra a descrição em linhas de no máximo 12 caracteres

        # Ajuste a posição inicial para a descrição com base no número de linhas
        num_linhas_descricao = len(descricao_linhas)
        y_position = 24 * mm + (num_linhas_descricao - 1) * 1 * mm  # Ajuste a posição inicial da descrição

        for linha in descricao_linhas:
            text_width = can.stringWidth(linha, "Scandia", 5)
            can.drawString(1 * mm, y_position, linha)
            y_position -= 6  # Ajuste o espaçamento entre linhas conforme necessário


    # Adicionar a descrição, data de admissão e número do usuário
    #can.setFont("Helvetica", 5)
    #can.setFillColor(white)  # Cor branca para a descrição
    #can.drawString(1 * mm, 25 * mm, descricao)


    if data_admissao:
        can.setFont("Scandia", 6)
        can.drawString(2 * mm, 11.5* mm, f"{data_admissao}")

    if id_usuario:
        can.setFont("Scandia_Bold", 10)
        can.drawString(42 * mm, 23.5 * mm, f"{id_usuario}")


    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfReader(packet)

    # Use the open template file directly
    existing_pdf = PdfReader(template_file)
    output = PdfWriter()

    # Add the first page (the card page)
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    if qrcode_base64:
    # Add the second page (QR code page)
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=(CARD_WIDTH, CARD_HEIGHT))

        # Adicionar o QR code no meio da segunda página

        qr_code_img = ImageReader(io.BytesIO(base64.b64decode(qrcode_base64)))


        # Adicionar o QR code no meio da segunda página
        qr_code_width = 40 * mm
        qr_code_height = 40 * mm
        can.drawImage(qr_code_img, CARD_WIDTH / 2 - qr_code_width / 2, CARD_HEIGHT / 2 - qr_code_height / 2, qr_code_width, qr_code_height)

        can.save()

        
        

        # Move to the beginning of the StringIO buffer
        packet.seek(0)
        new_pdf = PdfReader(packet)

        page = new_pdf.pages[0]
        output.add_page(page)

    # Finally, write "output" to a real file
    with open(output_path, "wb") as outputStream:
        output.write(outputStream)


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

import win32print
import win32ui
from PyPDF2 import PdfReader, PdfWriter
import os
from pdf2image import convert_from_path


def print_card(printer_name, filename):
    if not os.path.exists(filename):
        logger.error(f"O arquivo {filename} não foi encontrado.")
        raise FileNotFoundError(f"O arquivo {filename} não foi encontrado.")
    
    try:
        printers = get_printers()
        if printer_name not in printers:
            logger.error(f"A impressora '{printer_name}' não está instalada no sistema.")
            raise ValueError(f"A impressora '{printer_name}' não está instalada no sistema.")

        images = convert_from_path(filename)
        for i, image in enumerate(images):
            temp_image_filename = f'temp_page_{i}.png'
            image.save(temp_image_filename)

            # Imprimir a imagem
            # Aqui você deve adicionar o código para imprimir a imagem usando win32ui ou outra ferramenta

            os.remove(temp_image_filename)

        logger.info(f"O arquivo {filename} foi enviado para a impressora {printer_name}.")
    except Exception as e:
        logger.error(f"Ocorreu um erro ao tentar imprimir: {e}")
        raise






from django.shortcuts import render
from django.http import HttpResponse
import os
from .utils import dados_funcinario
import base64
from PyPDF2 import PdfReader, PdfWriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from reportlab.lib.utils import ImageReader
from PIL import Image
import os
from django.conf import settings


@user_in_groups(['rh', 'it'])
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

            template_path = os.path.join(settings.BASE_DIR, 'cartao', 'layout2.pdf')
            output_filename = f'cartao_{numero}.pdf'
            output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
            foto_path = None

            if not os.path.exists(settings.MEDIA_ROOT):
                os.makedirs(settings.MEDIA_ROOT)

            if foto_base64:
                foto_path = os.path.join(settings.MEDIA_ROOT, f'foto_{numero}.jpg')
                with open(foto_path, "wb") as foto_file:
                    foto_file.write(base64.b64decode(foto_base64))

            with open(template_path, "rb") as template_file:
                create_card(template_file, output_path, nome_usuario, id_usuario, descricao, data_admissao, foto_path, qrcode_base64 if qrcode_base64 else None)

            if foto_path:
                os.remove(foto_path)

            context = {
                'dados': dados,
                'numero': numero,
                'printers': printers,
                'preview': None,
                'download_link': f'{settings.MEDIA_URL}{output_filename}',
                'filename': output_filename
            }

            if 'print' in request.POST:
                print_card(printer_name, output_path)
                os.remove(output_path)
            return render(request, 'cartao/cartao.html', context)
        
        else:
            context = {'printers': printers, 'error_message': 'Nenhum funcionário encontrado com o número fornecido.'}
            return render(request, 'cartao/cartao.html', context)

    else:
        context = {'printers': printers}
        return render(request, 'cartao/cartao.html', context)



from django.http import FileResponse
import os



def download_pdf(request, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, filename)
    if os.path.exists(file_path):
        try:
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        except Exception as e:
            # Log do erro
            print(f"Erro ao enviar o arquivo: {e}")
            raise Http404("Arquivo não pôde ser enviado.")
    else:
        raise Http404("Arquivo não encontrado.")
    



    