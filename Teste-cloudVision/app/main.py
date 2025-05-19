import os
import io
import time
from PIL import Image, ImageFilter
from pdf2image import convert_from_path
from google.cloud import vision
from pergunta_gemini import perguntar_sobre_documento
from utils import carregar_variaveis

def main():
    config = carregar_variaveis()

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config["GOOGLE_CREDENTIALS"]
    client = vision.ImageAnnotatorClient()

    os.makedirs(config["TEXTOS_FOLDER"], exist_ok=True)
    os.makedirs(config["RESPOSTAS_FOLDER"], exist_ok=True)

    for filename in os.listdir(config["PDFS_FOLDER"]):
        if filename.lower().endswith(".pdf"):
            caminho_pdf = os.path.join(config["PDFS_FOLDER"], filename)
            print(f"📄 Processando {caminho_pdf}...")

            try:
                paginas = convert_from_path(caminho_pdf, dpi=300, poppler_path=config["POPPLER_PATH"])

                resultado = []
                imagem_paths = []

                for i, pagina in enumerate(paginas):
                    img = pagina.convert("L").filter(ImageFilter.SHARPEN)
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG")
                    image = vision.Image(content=buffer.getvalue())

                    image_context = vision.ImageContext(language_hints=["pt"])

                    max_tentativas = 3
                    tentativa = 0
                    sucesso = False
                    while tentativa < max_tentativas and not sucesso:
                        try:
                            response = client.document_text_detection(image=image, image_context=image_context)
                            texto = response.full_text_annotation.text
                            resultado.append(f"\n--- Página {i+1} ---\n{texto}\n")
                            sucesso = True
                        except Exception as e:
                            print(f"⚠️ Tentativa {tentativa+1} falhou ao processar página {i+1}: {e}")
                            tentativa += 1
                            time.sleep(2)

                    if not sucesso:
                        raise RuntimeError(f"❌ Falha ao processar a página {i+1} após várias tentativas.")

                    # Salva imagem temporária para usar no Gemini
                    img_path = os.path.join(config["TEXTOS_FOLDER"], f"{os.path.splitext(filename)[0]}_pagina{i+1}.jpg")
                    pagina.save(img_path, "JPEG")
                    imagem_paths.append(img_path)

                    time.sleep(1)

                # Salvar OCR como TXT
                txt_path = os.path.join(config["TEXTOS_FOLDER"], f"{os.path.splitext(filename)[0]}.txt")
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.writelines(resultado)
                print(f"✅ Texto salvo em {txt_path}")

                # Resumo automático
                resumo = perguntar_sobre_documento(imagem_paths, "Resuma o conteúdo principal deste documento.")
                print(f"\n📝 Resumo automático:\n{resumo}\n")

                resposta_path = os.path.join(config["RESPOSTAS_FOLDER"], f"{os.path.splitext(filename)[0]}_resumo.txt")
                with open(resposta_path, "w", encoding="utf-8") as f:
                    f.write(resumo)

                # Perguntas adicionais
                while True:
                    pergunta_usuario = input("❓ Deseja fazer uma pergunta sobre este documento? (Enter para pular): ").strip()
                    if not pergunta_usuario:
                        break
                    resposta = perguntar_sobre_documento(imagem_paths, pergunta_usuario)
                    print(f"\n💬 Resposta: {resposta}\n")

            except Exception as e:
                print(f"❌ Erro ao processar {filename}: {e}")

if __name__ == "__main__":
    main()