from flask import Flask, render_template, json, request, Response
from datetime import datetime, timedelta
import config
import banco
import requests
import logging
from werkzeug.exceptions import HTTPException
import re

app = Flask(__name__)

# Configuração de logging para registrar erros
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para validar e-mail
def validar_email(email):
    import re
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

# Handlers globais de erro
@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"Erro 400: {error}")
    return json.jsonify({'erro': 'Requisição inválida.'}), 400

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"Erro 404: {error}")
    return json.jsonify({'erro': 'Recurso não encontrado.'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    logger.warning(f"Erro 405: {error}")
    return json.jsonify({'erro': 'Método não permitido.'}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro 500: {error}")
    return json.jsonify({'erro': 'Erro interno do servidor. Tente novamente mais tarde.'}), 500

@app.get('/')
def index():
    hoje = datetime.today().strftime('%Y-%m-%d')
    return render_template('index/index.html', hoje=hoje)

@app.get('/sobre')
def sobre():
    return render_template('index/sobre.html', titulo='Sobre Nós')

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
    try:
        data_inicial_semana = (datetime.today() + timedelta(days=-6)).strftime('%Y-%m-%d')
        data_final_semana = datetime.today().strftime('%Y-%m-%d')
        maior_id = banco.obterIdMaximo("passagem")
        resultado = requests.get(f'{config.url_api}?sensor=passage&id_sensor=2&id_inferior={maior_id}')
        dados_novos = resultado.json()
        if dados_novos and len(dados_novos) > 0:
            banco.inserirDados(dados_novos)
        semana = banco.listarConsolidadoSemana(data_inicial_semana, data_final_semana)
        return json.jsonify({'semana': semana})
    except Exception as e:
        logger.error(f"Erro ao obter dados da semana: {e}")
        return json.jsonify({'erro': 'Erro ao obter dados da semana.'}), 500

@app.route("/obterDadosMensalDiaSemana")
def obterDadosMensalDiaSemana():
    try:
        data_inicial = request.args.get('data_inicial')
        data_final = request.args.get('data_final')
        dia_semana = request.args.get('dia_semana')
        if not data_inicial or not data_final or not dia_semana:
            return json.jsonify({"erro": "Parâmetros obrigatórios não informados."}), 400
        maior_id = banco.obterIdMaximo("passagem")
        resultado = requests.get(f'{config.url_api}?sensor=passage&id_sensor=2&id_inferior={maior_id}')
        dados_novos = resultado.json()
        if dados_novos and len(dados_novos) > 0:
            banco.inserirDados(dados_novos)
        mensal_dia_semana = banco.listarConsolidadoMensalDiaSemana(data_inicial, data_final, dia_semana)
        return json.jsonify({'mensal_dia_semana': mensal_dia_semana})
    except Exception as e:
        logger.error(f"Erro ao obter dados mensal por dia da semana: {e}")
        return json.jsonify({'erro': 'Erro ao obter dados mensal por dia da semana.'}), 500

@app.route("/obterDadosMensalPresenca")
def obterDadosMensalPresenca():
    try:
        data_inicial = request.args.get('data_inicial')
        data_final = request.args.get('data_final')
        if not data_inicial or not data_final:
            return json.jsonify({"erro": "Parâmetros obrigatórios não informados."}), 400
        maior_id = banco.obterIdMaximo("passagem")
        resultado = requests.get(f'{config.url_api}?sensor=passage&id_sensor=2&id_inferior={maior_id}')
        dados_novos = resultado.json()
        if dados_novos and len(dados_novos) > 0:
            banco.inserirDados(dados_novos)
        mensal_presenca = banco.listarConsolidadoMensalPresenca(data_inicial, data_final)
        return json.jsonify({'mensal_presenca': mensal_presenca})
    except Exception as e:
        logger.error(f"Erro ao obter dados mensal de presença: {e}")
        return json.jsonify({'erro': 'Erro ao obter dados mensal de presença.'}), 500

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
    try:
        contratantes = banco.listarContratantes()
        return json.jsonify(contratantes)
    except Exception as e:
        logger.error(f"Erro ao listar contratantes: {e}")
        return json.jsonify({'erro': 'Erro ao listar contratantes.'}), 500

@app.route('/api/contratantes/<int:id>', methods=['GET'])
def api_obter_contratante(id):
    try:
        contratante = banco.obterContratante(id)
        if contratante:
            return json.jsonify(contratante)
        return json.jsonify({"erro": "Contratante não encontrado"}), 404
    except Exception as e:
        logger.error(f"Erro ao obter contratante: {e}")
        return json.jsonify({'erro': 'Erro ao obter contratante.'}), 500

@app.route('/api/contratantes', methods=['POST'])
def api_criar_contratante():
    try:
        dados = request.get_json()
        nome = dados.get('nome')
        email = dados.get('email')
        empresa = dados.get('empresa')
        senha = dados.get('senha')
        
        if not nome or not email or not empresa:
            return json.jsonify({"erro": "Dados incompletos"}), 400
        if not validar_email(email):
            return json.jsonify({"erro": "E-mail inválido"}), 400
        if len(nome) > 100 or len(email) > 100 or len(empresa) > 100:
            return json.jsonify({"erro": "Nome, e-mail ou empresa muito longos (máx. 100 caracteres)"}), 400
        if senha is None or len(senha) < 4:
            return json.jsonify({"erro": "Senha deve ter pelo menos 4 caracteres"}), 400

        banco.criarContratante(nome, email, empresa, senha)
        return json.jsonify({"mensagem": "Contratante criado com sucesso"}), 201
    except Exception as e:
        logger.error(f"Erro ao criar contratante: {e}")
        return json.jsonify({'erro': 'Erro ao criar contratante.'}), 500

@app.route('/api/contratantes/<int:id>', methods=['PUT'])
def api_atualizar_contratante(id):
    try:
        dados = request.get_json()
        nome = dados.get('nome')
        email = dados.get('email')
        empresa = dados.get('empresa')
        senha = dados.get('senha')
        
        if not nome or not email or not empresa:
            return json.jsonify({"erro": "Dados incompletos"}), 400
        if not validar_email(email):
            return json.jsonify({"erro": "E-mail inválido"}), 400
        if len(nome) > 100 or len(email) > 100 or len(empresa) > 100:
            return json.jsonify({"erro": "Nome, e-mail ou empresa muito longos (máx. 100 caracteres)"}), 400

        banco.atualizarContratante(id, nome, email, empresa)
        return json.jsonify({"mensagem": "Contratante atualizado com sucesso"})
    except Exception as e:
        logger.error(f"Erro ao atualizar contratante: {e}")
        return json.jsonify({'erro': 'Erro ao atualizar contratante.'}), 500

@app.route('/api/contratantes/<int:id>', methods=['DELETE'])
def api_deletar_contratante(id):
    try:
        banco.deletarContratante(id)
        return json.jsonify({"mensagem": "Contratante removido com sucesso"})
    except Exception as e:
        logger.error(f"Erro ao deletar contratante: {e}")
        return json.jsonify({'erro': 'Erro ao deletar contratante.'}), 500


# dps de tudo
if __name__ == '__main__':
    app.run(host=config.host, port=config.port, debug=True)
