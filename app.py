from flask import Flask, render_template, json, request, Response
from datetime import datetime, timedelta
import config
import banco

app = Flask(__name__)

@app.get('/')
def index():
    hoje = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/index.html', hoje=hoje)

@app.get('/sobre')
def sobre():
    return render_template('index/sobre.html', titulo='Sobre Nós')

@app.get('/homeC')
def homeC():
    hoje = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/homeC.html', titulo='Home', hoje=hoje)

@app.get('/contratar')
def contratar():
    return render_template('index/contratar.html', titulo='Contratar')

@app.get('/login')
def login():
    return render_template('index/login.html', titulo='Login')

@app.route("/obterDados")
def obterDados():
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')
    dia_semana = request.args.get('dia_semana')

    if not data_inicial or not data_final or not dia_semana:
        return json.jsonify({"erro": "Parâmetros obrigatórios não informados."}), 400

    mensal_dia_semana = banco.listarConsolidadoMensalDiaSemana(data_inicial, data_final, dia_semana)
    mensal_presenca = banco.listarConsolidadoMensalPresenca(data_inicial, data_final)

    return json.jsonify({
        'mensal_dia_semana': mensal_dia_semana,
        'mensal_presenca': mensal_presenca,
    })

@app.get('/semana')
def semana():
    data_inicial = (datetime.today() + timedelta(days=-29)).strftime('%Y-%m-%d')
    data_final = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/semana.html', titulo='Consolidado por Semana', data_inicial=data_inicial, data_final=data_final)

@app.post('/criar')
def criar():
    dados = request.json
    print(dados.get('id'))
    print(dados.get('nome'))
    return Response(status=204)

if __name__ == '__main__':
    app.run(host=config.host, port=config.port, debug=True)