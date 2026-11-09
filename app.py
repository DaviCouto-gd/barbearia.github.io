import os
from datetime import datetime
 
import pymysql
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
 
# Lê o arquivo .env que fica na mesma pasta do app.py
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
 
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "troque-esta-chave")
 
# código gravado no banco -> nome mostrado na tela
SERVICO_NOMES = {
    "corte": "Corte Masculino",
    "barba": "Barba",
    "combo": "Corte + Barba",
    "infantil": "Corte Infantil",
    "fade": "Degradê / Fade",
    "outro": "Outro",
}
 
 
def conectar_bd():
    """Abre uma conexão com o MySQL da outra instância (dados vêm do .env)."""
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        # horário de Brasília nas datas lidas do banco (o servidor MySQL costuma usar UTC)
        init_command="SET time_zone = '-03:00'",
    )
 
 
def buscar_mensagens(limite=50):
    """Lê as últimas mensagens do banco. O telefone NÃO é buscado de propósito:
    a página do mural é pública."""
    conexao = conectar_bd()
    try:
        with conexao.cursor() as cursor:
            cursor.execute(
                "SELECT id, nome, servico, dia_preferido, mensagem, criado_em "
                "FROM mensagens ORDER BY id DESC LIMIT %s",
                (limite,),
            )
            linhas = cursor.fetchall()
    finally:
        conexao.close()
 
    return [
        {
            "id": l["id"],
            "nome": l["nome"],
            "servico": SERVICO_NOMES.get(l["servico"], ""),
            "dia": l["dia_preferido"].strftime("%d/%m/%Y") if l["dia_preferido"] else "",
            "mensagem": l["mensagem"] or "",
            "hora": l["criado_em"].strftime("%d/%m/%Y %H:%M") if l["criado_em"] else "",
        }
        for l in linhas
    ]
 
 
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
 
        if servico not in SERVICO_NOMES:
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
            flash("Mensagem enviada! Ela já aparece no mural de mensagens.", "sucesso")
        except pymysql.MySQLError:
            app.logger.exception("Erro ao salvar a mensagem no MySQL")
            flash("Não foi possível enviar agora. Tente de novo ou chame no WhatsApp.", "erro")
        finally:
            if conexao:
                conexao.close()
 
        # Redireciona para evitar reenviar o formulário ao atualizar a página (F5)
        return redirect(url_for("contato"))
 
    return render_template("contato.html")
 
 
@app.route("/mensagens")
def mensagens():
    """5ª página: mural público com as mensagens gravadas no banco."""
    try:
        lista = buscar_mensagens()
        erro_banco = False
    except pymysql.MySQLError:
        app.logger.exception("Erro ao ler as mensagens do MySQL")
        lista = []
        erro_banco = True
    return render_template("mensagens.html", mensagens=lista, erro_banco=erro_banco)
 
 
@app.route("/api/mensagens")
def api_mensagens():
    """Devolve as mensagens em JSON. O JavaScript da página chama isto a cada 5 s."""
    try:
        lista = buscar_mensagens()
    except pymysql.MySQLError:
        app.logger.exception("Erro ao ler as mensagens do MySQL")
        return jsonify(erro="banco indisponivel"), 503
    resposta = jsonify(mensagens=lista)
    resposta.headers["Cache-Control"] = "no-store"
    return resposta
 
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
