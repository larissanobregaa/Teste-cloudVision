import os
import io
from PIL import Image, ImageFilter
from pdf2image import convert_from_path
from google.cloud import vision
from pergunta_gemini import perguntar_sobre_documento

# Configurações de caminho
CREDENTIAL_PATH = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\Teste-cloudVision\credenciais\primeiro-teste-456814-f1c10b6e1f97.json"
POPPLER_PATH = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\poppler-24.08.0\Library\bin"
PDFS_FOLDER = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\Teste-cloudVision\imagens"
OUTPUT_FOLDER = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\Teste-cloudVision\extracoes"
IMAGENS_CONVERTIDAS_FOLDER = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\Teste-cloudVision\imagens_convertidas"
RESPOSTAS_FOLDER = r"C:\Users\Larissa Nobrega\Documents\Projetos\Teste-cloudVision\Teste-cloudVision\respostas"

# Verificações
if not os.path.exists(CREDENTIAL_PATH):
    raise FileNotFoundError(f"Credencial não encontrada: {CREDENTIAL_PATH}")
if not os.path.exists(POPPLER_PATH):
    raise FileNotFoundError(f"Poppler não encontrado: {POPPLER_PATH}")
if not os.path.exists(PDFS_FOLDER):
    raise FileNotFoundError(f"Pasta de PDFs não encontrada: {PDFS_FOLDER}")

# Variável de ambiente do Google
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIAL_PATH

# Criação de pastas
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(IMAGENS_CONVERTIDAS_FOLDER, exist_ok=True)
os.makedirs(RESPOSTAS_FOLDER, exist_ok=True)

# Cliente do Vision
client = vision.ImageAnnotatorClient()

if __name__ == "__main__":
    for filename in os.listdir(PDFS_FOLDER):
        if filename.lower().endswith('.pdf'):
            caminho_pdf = os.path.join(PDFS_FOLDER, filename)
            print(f"📄 Processando {caminho_pdf}...")

            try:
                paginas = convert_from_path(caminho_pdf, dpi=300, poppler_path=POPPLER_PATH)

                # OCR
                resultado = []
                imagem_paths = []
                for i, pagina in enumerate(paginas):
                    img = pagina.convert("L").filter(ImageFilter.SHARPEN)
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG")
                    image = vision.Image(content=buffer.getvalue())

                    image_context = vision.ImageContext(language_hints=["pt"])
                    response = client.document_text_detection(image=image, image_context=image_context)
                    texto = response.full_text_annotation.text
                    resultado.append(f"\n--- Página {i+1} ---\n{texto}\n")

                    # Salvar imagem
                    img_path = os.path.join(IMAGENS_CONVERTIDAS_FOLDER, f"{os.path.splitext(filename)[0]}_pagina{i+1}.jpg")
                    pagina.save(img_path, "JPEG")
                    imagem_paths.append(img_path)

                # Salvar OCR em TXT
                nome_arquivo_txt = os.path.splitext(filename)[0] + '.txt'
                caminho_saida = os.path.join(OUTPUT_FOLDER, nome_arquivo_txt)
                with open(caminho_saida, "w", encoding="utf-8") as f:
                    for texto in resultado:
                        f.write(texto)
                print(f"✅ Extração salva em {caminho_saida}")

                # Geração de resumo automático
                resumo = perguntar_sobre_documento(imagem_paths, "Resuma o conteúdo principal deste documento.")
                print(f"\n📝 Resumo automático:\n{resumo}\n")

                # Salvar o resumo
                resposta_path = os.path.join(RESPOSTAS_FOLDER, f"{os.path.splitext(filename)[0]}_resumo.txt")
                with open(resposta_path, "w", encoding="utf-8") as resp_file:
                    resp_file.write(resumo)

                # Pergunta adicional opcional
                while True:
                    pergunta_usuario = input("❓ Deseja fazer uma pergunta sobre este documento? (pressione Enter para pular): ").strip()
                    if not pergunta_usuario:
                        break
                    resposta = perguntar_sobre_documento(imagem_paths, pergunta_usuario)
                    print(f"\n💬 Resposta: {resposta}\n")

            except Exception as e:
                print(f"❌ Erro ao processar {filename}: {e}")
