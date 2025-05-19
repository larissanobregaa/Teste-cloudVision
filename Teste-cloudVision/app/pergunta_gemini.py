import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def perguntar_sobre_documento(lista_caminhos_imagens, pergunta):
    imagens = []
    for caminho in lista_caminhos_imagens:
        with open(caminho, "rb") as f:
            imagens.append({
                "mime_type": "image/jpeg",
                "data": f.read()
            })

    
    model = genai.GenerativeModel("gemini-2.0-flash")
    resposta = model.generate_content([*imagens, pergunta])

    return resposta.text
