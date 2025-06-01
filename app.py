from flask import Flask, render_template, json, request, Response
from datetime import datetime, timedelta
import config
import banco
import requests

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

@app.get('/dashboard')
def dashboard():
    return render_template('index/dashboard.html', titulo='Dashboard')

@app.get('/registrar')
def registrar():
    return render_template('index/registrar.html', titulo='Cadastro')

@app.route("/obterDadosSemana")
def obterDadosSemana():
    #data_final = request.args['data']
    #data_inicial = (datetime.strptime(data_final, '%Y-%m-%d') + timedelta(days=-6)).strftime('%Y-%m-%d')
    data_inicial_semana = (datetime.today() + timedelta(days=-6)).strftime('%Y-%m-%d')
    data_final_semana = datetime.today().strftime('%Y-%m-%d')

    # Obter o maior id do banco
    maior_id = banco.obterIdMaximo("passagem")

    # Buscar dados novos da API externa
    resultado = requests.get(f'{config.url_api}?sensor=passage&id_sensor=2&id_inferior={maior_id}')
    dados_novos = resultado.json()

    # Inserir os dados novos no banco
    if dados_novos and len(dados_novos) > 0:
        banco.inserirDados(dados_novos)

    semana = banco.listarConsolidadoSemana(data_inicial_semana, data_final_semana)

    return json.jsonify({
        'semana': semana
    })

@app.route("/obterDadosMensalDiaSemana")
def obterDadosMensalDiaSemana():
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')
    dia_semana = request.args.get('dia_semana')

    if not data_inicial or not data_final or not dia_semana:
        return json.jsonify({"erro": "Parâmetros obrigatórios não informados."}), 400

    # Obter o maior id do banco
    maior_id = banco.obterIdMaximo("passagem")

    # Buscar dados novos da API externa
    resultado = requests.get(f'{config.url_api}?sensor=passage&id_sensor=2&id_inferior={maior_id}')
    dados_novos = resultado.json()

    # Inserir os dados novos no banco
    if dados_novos and len(dados_novos) > 0:
        banco.inserirDados(dados_novos)

    mensal_dia_semana = banco.listarConsolidadoMensalDiaSemana(data_inicial, data_final, dia_semana)

    return json.jsonify({
        'mensal_dia_semana': mensal_dia_semana,
    })

@app.route("/obterDadosMensalPresenca")
def obterDadosMensalPresenca():
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')

    if not data_inicial or not data_final:
        return json.jsonify({"erro": "Parâmetros obrigatórios não informados."}), 400

    # Obter o maior id do banco
    maior_id = banco.obterIdMaximo("passagem")

    # Buscar dados novos da API externa
    resultado = requests.get(f'{config.url_api}?sensor=passage&id_sensor=2&id_inferior={maior_id}')
    dados_novos = resultado.json()

    # Inserir os dados novos no banco
    if dados_novos and len(dados_novos) > 0:
        banco.inserirDados(dados_novos)

    mensal_presenca = banco.listarConsolidadoMensalPresenca(data_inicial, data_final)

    return json.jsonify({
        'mensal_presenca': mensal_presenca,
    })

@app.get('/semana')
def semana():
    data_inicial = (datetime.today() + timedelta(days=-29)).strftime('%Y-%m-%d')
    data_final = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/semana.html', titulo='Consolidado por Semana', data_inicial=data_inicial, data_final=data_final)

@app.get('/mensalDiaSemana')
def mensalDiaSemana():
    data_inicial = (datetime.today() + timedelta(days=-29)).strftime('%Y-%m-%d')
    data_final = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/mensalDiaSemana.html', titulo='Consolidado por Dia da Semana', data_inicial=data_inicial, data_final=data_final)

@app.get('/mensalPresenca')
def mensalPresenca():
    data_inicial = (datetime.today() + timedelta(days=-19)).strftime('%Y-%m-%d')
    data_final = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/mensalPresenca.html', titulo='Presença por Dia', data_inicial=data_inicial, data_final=data_final)

@app.post('/criar')
def criar():
    dados = request.json
    print(dados.get('id'))
    print(dados.get('nome'))
    return Response(status=204)

# if __name__ == '__main__':
#     app.run(host=config.host, port=config.port, debug=True)


# ROTAS - CONTRATANTE

@app.route('/api/contratantes', methods=['GET'])
def api_listar_contratantes():
    contratantes = banco.listarContratantes()
    return json.jsonify(contratantes)

@app.route('/api/contratantes/<int:id>', methods=['GET'])
def api_obter_contratante(id):
    contratante = banco.obterContratante(id)
    if contratante:
        return json.jsonify(contratante)
    return json.jsonify({"erro": "Contratante não encontrado"}), 404

@app.route('/api/contratantes', methods=['POST'])
def api_criar_contratante():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    empresa = dados.get('empresa')
    senha = dados.get('senha')
    
    if not nome or not email or not empresa:
        return json.jsonify({"erro": "Dados incompletos"}), 400

    banco.criarContratante(nome, email, empresa, senha)
    return json.jsonify({"mensagem": "Contratante criado com sucesso"}), 201

@app.route('/api/contratantes/<int:id>', methods=['PUT'])
def api_atualizar_contratante(id):
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    empresa = dados.get('empresa')
    senha = dados.get('senha')
    
    if not nome or not email or not empresa:
        return json.jsonify({"erro": "Dados incompletos"}), 400

    banco.atualizarContratante(id, nome, email, empresa)
    return json.jsonify({"mensagem": "Contratante atualizado com sucesso"})

@app.route('/api/contratantes/<int:id>', methods=['DELETE'])
def api_deletar_contratante(id):
    banco.deletarContratante(id)
    return json.jsonify({"mensagem": "Contratante removido com sucesso"})


# dps de tudo
if __name__ == '__main__':
    app.run(host=config.host, port=config.port, debug=True)
