import os
from datetime import datetime

import pymysql
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash

# Lê o arquivo .env que fica na mesma pasta do app.py
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "troque-esta-chave")

SERVICOS_VALIDOS = {"corte", "barba", "combo", "infantil", "fade", "outro"}


def conectar_bd():
    """Abre uma conexão com o MySQL da outra instância (dados vêm do .env)."""
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/servicos")
def servicos():
    return render_template("servicos.html")


@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


@app.route("/contato", methods=["GET", "POST"])
def contato():
    # GET  -> só mostra a página com o formulário
    # POST -> recebe os dados do formulário e guarda no MySQL
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()[:100]
        telefone = request.form.get("telefone", "").strip()[:20]
        servico = request.form.get("servico", "").strip()
        mensagem = request.form.get("mensagem", "").strip()[:1000]
        dia_texto = request.form.get("dia", "").strip()

        if servico not in SERVICOS_VALIDOS:
            servico = None

        try:
            dia = datetime.strptime(dia_texto, "%Y-%m-%d").date() if dia_texto else None
        except ValueError:
            dia = None

        if not nome:
            flash("Por favor, informe o seu nome.", "erro")
            return redirect(url_for("contato"))

        conexao = None
        try:
            conexao = conectar_bd()
            with conexao.cursor() as cursor:
                sql = (
                    "INSERT INTO mensagens (nome, telefone, servico, dia_preferido, mensagem) "
                    "VALUES (%s, %s, %s, %s, %s)"
                )
                cursor.execute(sql, (nome, telefone, servico, dia, mensagem))
            conexao.commit()
            flash("Mensagem enviada! Entraremos em contato em breve.", "sucesso")
        except pymysql.MySQLError:
            app.logger.exception("Erro ao salvar a mensagem no MySQL")
            flash("Não foi possível enviar agora. Tente de novo ou chame no WhatsApp.", "erro")
        finally:
            if conexao:
                conexao.close()

        # Redireciona para evitar reenviar o formulário ao atualizar a página (F5)
        return redirect(url_for("contato"))

    return render_template("contato.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
