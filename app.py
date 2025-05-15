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

@app.route("/obterDados")
def obterDados():
    #data_final = request.args['data']
    #data_inicial = (datetime.strptime(data_final, '%Y-%m-%d') + timedelta(days=-6)).strftime('%Y-%m-%d')
    data_inicial_semana = (datetime.today() + timedelta(days=-6)).strftime('%Y-%m-%d')
    data_final_semana = datetime.today().strftime('%Y-%m-%d')

    data_inicial = request.args['data_inicial']
    data_final = request.args['data_final']
    dia_semana = request.args['dia_semana']

    # Obter o maior id do banco
    maior_id = banco.obterIdMaximo("passagem")

    resultado = requests.get(f'{config.url_api}?sensor=passage&id_sensor=2&id_inferior={maior_id}')
    dados_novos = resultado.json()

    # Inserir os dados novos no banco
    if dados_novos and len(dados_novos) > 0:
        banco.inserirDados(dados_novos)

    # Trazer os dados do banco
    semana = banco.listarConsolidadoSemana(data_inicial_semana, data_final_semana)
    mensal_dia_semana = banco.listarConsolidadoMensalDiaSemana(data_inicial, data_final, dia_semana)
    mensal_presenca = banco.listarConsolidadoMensalPresenca(data_inicial, data_final)

    return json.jsonify({
        'semana': semana,
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
    print(dados['id'])
    print(dados['nome'])
    return Response(status=204)

if __name__ == '__main__':
    app.run(host=config.host, port=config.port, debug=True)