from flask import Flask, render_template, request, jsonify  # type: ignore
from pypdf import PdfReader
from transformers import pipeline

app = Flask(__name__)

# Carrega modelo de resumo (HuggingFace)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Página inicial -> carrega o HTML do chat
@app.route("/")
def index():
    return render_template("index.html")

# Rota do BOT -> recebe mensagem e responde
@app.route("/bot", methods=["POST"])
def bot():
    try:
        dados = request.get_json(force=True)  # força leitura do JSON
        print("📥 Recebido do usuário:", dados)

        texto_usuario = dados.get("mensagem", "").lower()

        if "oi" in texto_usuario or "olá" in texto_usuario:
            resposta = "Oi 👋! Como posso te ajudar?"
        elif "até que horas" in texto_usuario:
            resposta = "Nosso atendimento é de segunda a sexta, das 8h às 18h."
        elif "suporte" in texto_usuario:
            resposta = "Você precisa de suporte técnico ou financeiro?"
        else:
            resposta = "Desculpe, não entendi. Pode reformular?"

        print("📤 Respondendo:", resposta)
        return jsonify({"resposta": resposta})

    except Exception as e:
        print("❌ Erro no backend:", e)
        return jsonify({"resposta": "Erro interno no servidor."}), 500


# 🚀 Nova rota: upload de PDF e resumo
@app.route("/upload", methods=["POST"])
def upload_pdf():
    try:
        if "file" not in request.files:
            return jsonify({"resumo": "Nenhum arquivo enviado."})

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"resumo": "Arquivo inválido."})

        # Lê o PDF
        pdf = PdfReader(file)
        texto = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                texto += page_text + " "

        if not texto.strip():
            return jsonify({"resumo": "Não consegui extrair texto desse PDF."})

        # Limita o tamanho para não travar o modelo
        if len(texto) > 2000:
            texto = texto[:2000]

        # Resumir com HuggingFace
        resumo = summarizer(texto, max_length=150, min_length=50, do_sample=False)

        return jsonify({"resumo": resumo[0]["summary_text"]})

    except Exception as e:
        print("❌ Erro ao processar PDF:", e)
        return jsonify({"resumo": "Erro ao processar PDF."}), 500


if __name__ == "__main__":
    
    app.run(debug=True)


