# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"credenciais\primeiro-teste-456814-f1c10b6e1f97.json"
# from google.cloud import vision
# import io
# from PIL import Image
# from pdf2image import convert_from_path

# Inicializa o cliente da API
# client = vision.ImageAnnotatorClient()

# Função para processar imagens (JPG, PNG, etc.)
# def processar_imagem_vision(caminho_imagem):
# with io.open(caminho_imagem, 'rb') as image_file:
# content = image_file.read()

# image = vision.Image(content=content)
# response = client.text_detection(image=image)
# textos = response.text_annotations

# if textos:
# return textos[0].description
# else:
# return "[Nenhum texto detectado]"

# Função para processar PDFs
# def processar_pdf(caminho_pdf):
# paginas = convert_from_path(caminho_pdf, dpi=300)
# textos = []

# for i, pagina in enumerate(paginas, 1):
# imagem_caminho = f"pagina_temp_{i}.jpg"
# pagina.save(imagem_caminho, "JPEG")
# texto = processar_imagem_vision(imagem_caminho)
# textos.append((i, texto))
# os.remove(imagem_caminho)

# return textos

# Caminho da pasta com arquivos
# pasta = "imagens"

# Processar todos os arquivos
# for arquivo in os.listdir(pasta):
# caminho = os.path.join(pasta, arquivo)
# if arquivo.lower().endswith(".pdf"):
# print(f"\n PDF: {arquivo}")
# textos = processar_pdf(caminho)
# for i, texto in textos:
# print(f"\nPágina {i}:\n{texto}\n" + "-" * 40)
# elif arquivo.lower().endswith((".jpg", ".png", ".jpeg")):
# print(f"\n Imagem: {arquivo}")
# texto = processar_imagem_vision(caminho)
# print(texto)
# print("-" * 40)
# else:
# print(f"Formato não suportado: {arquivo}")


import os
import io
from PIL import Image, ImageFilter
from pdf2image import convert_from_path
from google.cloud import vision


CREDENTIAL_PATH = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\Teste-cloudVision\credenciais\primeiro-teste-456814-f1c10b6e1f97.json"
POPPLER_PATH = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\poppler-24.08.0\Library\bin"
PDF_PATH = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\Teste-cloudVision\imagens\10211872_BR76036_Certidões_Matricula_Imovel.pdf"


if not os.path.exists(CREDENTIAL_PATH):
    raise FileNotFoundError(
        f"Arquivo de credenciais não encontrado: {CREDENTIAL_PATH}")
if not os.path.exists(POPPLER_PATH):
    raise FileNotFoundError(f"Pasta do Poppler não encontrada: {POPPLER_PATH}")
if not os.path.exists(PDF_PATH):
    raise FileNotFoundError(f"Arquivo PDF não encontrado: {PDF_PATH}")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIAL_PATH


client = vision.ImageAnnotatorClient()


def processar_pdf_vision(caminho_pdf):
    paginas = convert_from_path(
        caminho_pdf, dpi=300, poppler_path=POPPLER_PATH)
    textos = []

    for i, pagina in enumerate(paginas):
        img = pagina.convert("L").filter(ImageFilter.SHARPEN)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        image = vision.Image(content=buffer.getvalue())

        image_context = vision.ImageContext(language_hints=["pt"])

        response = client.document_text_detection(
            image=image, image_context=image_context)
        texto = response.full_text_annotation.text
        textos.append(texto)
        print(f"\n--- Página {i+1} ---\n{texto}\n")

    return textos



if __name__ == "__main__":
    resultado = processar_pdf_vision(PDF_PATH)
    # Se quiser salvar o texto em um arquivo:
    with open("texto_extraido.txt", "w", encoding="utf-8") as f:
        for i, texto in enumerate(resultado):
            f.write(f"\n--- Página {i+1} ---\n{texto}\n")
    print("Extração concluída e salva em texto_extraido.txt")



# Pasta com arquivos
# pasta = "imagens"

# Loop em todos os arquivos da pasta
# for arquivo in os.listdir(pasta):
    # caminho = os.path.join(pasta, arquivo)

    # if arquivo.lower().endswith(".pdf"):
    # print(f"\n PDF: {arquivo}")
    # paginas = processar_pdf_vision(caminho)
    # for i, texto in paginas:
    # print(f"\nPágina {i}:\n{texto}\n" + "-" * 50)

    # elif arquivo.lower().endswith((".jpg", ".png", ".jpeg")):
    # print(f"\n Imagem: {arquivo}")
    # texto = processar_imagem_vision(caminho)
    # print(texto)
    # print("-" * 50)

    # else:
    # print(f"\n Arquivo não suportado: {arquivo}")
