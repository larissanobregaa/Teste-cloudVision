import os
import io
from PIL import Image, ImageFilter
from pdf2image import convert_from_path
from google.cloud import vision

CREDENTIAL_PATH = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\Teste-cloudVision\credenciais\primeiro-teste-456814-f1c10b6e1f97.json"
POPPLER_PATH = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\poppler-24.08.0\Library\bin"
PDFS_FOLDER = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\Teste-cloudVision\imagens"
OUTPUT_FOLDER = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\Teste-cloudVision\extracoes"

# Verificações
if not os.path.exists(CREDENTIAL_PATH):
    raise FileNotFoundError(f"Arquivo de credenciais não encontrado: {CREDENTIAL_PATH}")
if not os.path.exists(POPPLER_PATH):
    raise FileNotFoundError(f"Pasta do Poppler não encontrada: {POPPLER_PATH}")
if not os.path.exists(PDFS_FOLDER):
    raise FileNotFoundError(f"Pasta de PDFs não encontrada: {PDFS_FOLDER}")

# Configura variável de ambiente
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIAL_PATH

# Instancia cliente da API
client = vision.ImageAnnotatorClient()

def processar_pdf_vision(caminho_pdf):
    paginas = convert_from_path(caminho_pdf, dpi=300, poppler_path=POPPLER_PATH)
    textos = []

    for i, pagina in enumerate(paginas):
        img = pagina.convert("L").filter(ImageFilter.SHARPEN)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        image = vision.Image(content=buffer.getvalue())

        image_context = vision.ImageContext(language_hints=["pt"])

        response = client.document_text_detection(image=image, image_context=image_context)
        texto = response.full_text_annotation.text
        textos.append(f"\n--- Página {i+1} ---\n{texto}\n")

    return textos

if __name__ == "__main__":
    # Cria a pasta de saída se não existir
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Processa todos os PDFs da pasta
    for filename in os.listdir(PDFS_FOLDER):
        if filename.lower().endswith('.pdf'):
            caminho_pdf = os.path.join(PDFS_FOLDER, filename)
            print(f"Processando {caminho_pdf}...")

            try:
                resultado = processar_pdf_vision(caminho_pdf)

                # Nome do .txt com o mesmo nome do PDF
                nome_arquivo_txt = os.path.splitext(filename)[0] + '.txt'
                caminho_saida = os.path.join(OUTPUT_FOLDER, nome_arquivo_txt)

                with open(caminho_saida, "w", encoding="utf-8") as f:
                    for texto in resultado:
                        f.write(texto)

                print(f"Extração concluída e salva em {caminho_saida}\n")

            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")
