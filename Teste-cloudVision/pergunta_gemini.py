import google.generativeai as genai


genai.configure(api_key="AIzaSyC_z7lB90f9qJiefIsoZ_Ho-tULERV_3ck")

def perguntar_sobre_documento(lista_caminhos_imagens, pergunta):
    imagens = []
    for caminho in lista_caminhos_imagens:
        with open(caminho, "rb") as f:
            imagens.append({
                "mime_type": "image/jpeg",
                "data": f.read()
            })

    
    model = genai.GenerativeModel("gemini-1.5-pro")
    resposta = model.generate_content([*imagens, pergunta])

    return resposta.text
