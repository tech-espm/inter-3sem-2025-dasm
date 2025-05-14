from flask import Flask, render_template, json, request, Response
import config
import requests
from datetime import datetime, timedelta
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
    return render_template('index/homeC.html', titulo='Home')

@app.get('/contratar')
def contratar():
    return render_template('index/contratar.html', titulo='Contratar')

@app.get('/login')
def login():
    return render_template('index/login.html', titulo='Login')

@app.route("/obterDadosSemana")
def obterDadosSemana():
    data_final = request.args['data']
    data_inicial = (datetime.strptime(data_final, '%Y-%m-%d') + timedelta(days=-6)).strftime('%Y-%m-%d')

    # Obter o maior id do banco
    maior_id = banco.obterIdMaximo("passagem")

    resultado = requests.get(f'{config.url_api}?sensor=passage&id_sensor=2&id_inferior={maior_id}')
    dados_novos = resultado.json()

	# Inserir os dados novos no banco
    if dados_novos and len(dados_novos) > 0:
        banco.inserirDados(dados_novos)

    # Trazer os dados do banco
    dados = banco.listarConsolidadoSemana(data_inicial, data_final)

    return json.jsonify(dados)

@app.get('/semana')
def semana():
    semana_passada = (datetime.today() + timedelta(days=-6)).strftime('%Y-%m-%d')
    hoje = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/semana.html', titulo='Consolidado por Semana', semana_passada=semana_passada, hoje=hoje)

@app.post('/criar')
def criar():
    dados = request.json
    print(dados['id'])
    print(dados['nome'])
    return Response(status=204)

if __name__ == '__main__':
    app.run(host=config.host, port=config.port, debug=True)