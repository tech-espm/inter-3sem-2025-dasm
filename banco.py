# Vamos utilizar o pacote SQLAlchemy para acesso a banco de dados:
# https://docs.sqlalchemy.org
#
# Para isso, ele precisa ser instalado via pip (de preferência com o VS Code fechado):
# python -m pip install SQLAlchemy
#
# Além disso, o SQLAlchemy precisa de um driver do conexão ao banco. Isso depende do servidor
# (MySQL, Postgres, SQL Server, Oracle...) e do driver real. Vamos utilizar o driver MySQL-Connector,
# que também precisa ser instalado (de preferência com o VS Code fechado):
# python -m pip install mysql-connector-python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from config import conexao_banco
import logging

logger = logging.getLogger(__name__)

# Como criar uma comunicação com o banco de dados:
# https://docs.sqlalchemy.org/en/14/core/engines.html
#
# Detalhes específicos ao MySQL
# https://docs.sqlalchemy.org/en/14/dialects/mysql.html#module-sqlalchemy.dialects.mysql.mysqlconnector
#
# mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
engine = create_engine(conexao_banco)

# A função text(), utilizada ao longo desse código, serve para encapsular um comando
# SQL qualquer, de modo que o SQLAlchemy possa entender!

def listarPessoas():
    try:
        with Session(engine) as sessao:
            pessoas = sessao.execute(text("SELECT id, nome, email FROM pessoa ORDER BY nome"))
            for (id, nome, email) in pessoas:
                print(f'\nid: {id} / nome: {nome} / email: {email}')
    except Exception as e:
        logger.error(f"Erro ao listar pessoas: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def obterPessoa(id):
    try:
        with Session(engine) as sessao:
            parametros = {'id': id}
            pessoa = sessao.execute(text("SELECT id, nome, email FROM pessoa WHERE id = :id"), parametros).first()
            if pessoa == None:
                print('Pessoa não encontrada!')
            else:
                print(f'\nid: {pessoa.id} / nome: {pessoa.nome} / email: {pessoa.email}')
    except Exception as e:
        logger.error(f"Erro ao obter pessoa: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def criarPessoa(nome, email):
    try:
        validar_pessoa(nome, email)
        with Session(engine) as sessao, sessao.begin():
            pessoa = {'nome': nome, 'email': email}
            sessao.execute(text("INSERT INTO pessoa (nome, email) VALUES (:nome, :email)"), pessoa)
    except ValueError as ve:
        logger.warning(f"Validação falhou ao criar pessoa: {ve}")
        raise
    except Exception as e:
        logger.error(f"Erro ao criar pessoa: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def obterIdMaximo(tabela):
    try:
        with Session(engine) as sessao:
            registro = sessao.execute(text(f"SELECT MAX(id) id FROM {tabela}")).first()
            if registro == None or registro.id == None:
                return 0
            else:
                return registro.id
    except Exception as e:
        logger.error(f"Erro ao obter id máximo da tabela {tabela}: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def inserirDados(registros):
    try:
        with Session(engine) as sessao, sessao.begin():
            for registro in registros:
                validar_registro_passagem(registro)
                sessao.execute(text("INSERT INTO passagem (id, data, id_sensor, delta, bateria, entrada, saida) VALUES (:id, :data, :id_sensor, :delta, :bateria, :entrada, :saida)"), registro)
    except ValueError as ve:
        logger.warning(f"Validação falhou ao inserir dados de passagem: {ve}")
        raise
    except Exception as e:
        logger.error(f"Erro ao inserir dados: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def listarConsolidadoSemana(data_inicial, data_final):
    try:
        with Session(engine) as sessao:
            parametros = {
                'data_inicial': data_inicial + ' 00:00:00',
                'data_final': data_final + ' 23:59:59'
            }
            registros = sessao.execute(text("""
            select dayofweek(data) dia_semana, extract(hour from data) hora, cast(sum(entrada + saida) as signed) total
            from passagem
            where data between :data_inicial and :data_final
            and id_sensor = 2
            group by dia_semana, hora
            """), parametros)
            lista = []
            for (dia_semana, hora, total) in registros:
                lista.append({
                    "dia_semana": dia_semana,
                    "hora": hora,
                    "total": total
                })
            return lista
    except Exception as e:
        logger.error(f"Erro ao listar consolidado da semana: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def listarConsolidadoMensalDiaSemana(data_inicial, data_final, dia_semana):
    try:
        with Session(engine) as sessao:
            parametros = {
                'data_inicial': data_inicial + ' 00:00:00',
                'data_final': data_final + ' 23:59:59',
                'dia_semana': dia_semana
            }
            registros = sessao.execute(text("""
            select date_format(date(data), '%d/%m/%Y') dia, extract(hour from data) hora, cast(sum(entrada + saida) as signed) total
            from passagem
            where data between :data_inicial and :data_final
            and dayofweek(data) = :dia_semana
            and id_sensor = 2
            group by dia, hora
            """), parametros)
            lista = []
            for (dia, hora, total) in registros:
                lista.append({
                    "dia": dia,
                    "hora": hora,
                    "total": total
                })
            return lista
    except Exception as e:
        logger.error(f"Erro ao listar consolidado mensal por dia da semana: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def listarConsolidadoMensalPresenca(data_inicial, data_final):
    try:
        with Session(engine) as sessao:
            parametros = {
                'data_inicial': data_inicial + ' 00:00:00',
                'data_final': data_final + ' 23:59:59'
            }
            registros = sessao.execute(text("""
            select date_format(date(data), '%d/%m') dia, extract(hour from data) hora, cast(sum(entrada) as signed) total_entrada, cast(sum(saida) as signed) total_saida
            from passagem
            where data between :data_inicial and :data_final
            and id_sensor = 2
            group by dia, hora
            order by dia, hora;
            """), parametros)
            lista = []
            for (dia, hora, total_entrada, total_saida) in registros:
                lista.append({
                    "dia": dia,
                    "hora": hora,
                    "total_entrada": total_entrada,
                    "total_saida": total_saida
                })
            return lista
    except Exception as e:
        logger.error(f"Erro ao listar consolidado mensal de presença: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

# ------------------------------
#   CRUD NÃO - CONTRATANTES
#-------------------------------

def listarContratantes():
    try:
        with Session(engine) as sessao:
            resultado = sessao.execute(text("""
                SELECT id, nome, email, empresa FROM contratante ORDER BY nome """))
            contratantes = []
            for id, nome, email, empresa in resultado:
                contratantes.append({
                    'id': id,
                    'nome': nome,
                    'email': email,
                    'empresa': empresa})
        return contratantes
    except Exception as e:
        logger.error(f"Erro ao listar contratantes: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def obterContratante(id):
    try:
        with Session(engine) as sessao:
            resultado = sessao.execute(text("""
                SELECT id, nome, email, empresa FROM contratante WHERE id = :id"""), {'id': id}).first()
            if resultado:
                return {
                    'id': resultado.id,
                    'nome': resultado.nome,
                    'email': resultado.email,
                    'empresa': resultado.empresa
                }
        return None
    except Exception as e:
        logger.error(f"Erro ao obter contratante: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def criarContratante(nome, email, empresa, senha):
    try:
        with Session(engine) as sessao, sessao.begin():
            sessao.execute(text("""
                INSERT INTO contratante(nome, email, empresa, senha)
                VALUES (:nome, :email, :empresa, :senha)"""),
                {'nome': nome, 'email': email, 'empresa': empresa, 'senha': senha})
    except Exception as e:
        logger.error(f"Erro ao criar contratante: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def atualizarContratante(id, nome, email, empresa):
    try:
        with Session(engine) as sessao, sessao.begin():
            sessao.execute(text("""
                UPDATE contratante
                SET nome = :nome, email = :email, empresa = :empresa
                WHERE id = :id"""),
                {'id': id, 'nome': nome, 'email': email, 'empresa': empresa})
    except Exception as e:
        logger.error(f"Erro ao atualizar contratante: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def deletarContratante(id):
    try:
        with Session(engine) as sessao, sessao.begin():
            sessao.execute(text(""" DELETE FROM contratante WHERE id = :id """), {'id': id})
    except Exception as e:
        logger.error(f"Erro ao deletar contratante: {e}")
        raise Exception("Erro ao acessar o banco de dados.")

def validar_email(email):
    import re
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

def validar_pessoa(nome, email):
    if not nome or not email:
        raise ValueError("Nome e e-mail são obrigatórios.")
    if not validar_email(email):
        raise ValueError("E-mail inválido.")
    if len(nome) > 100 or len(email) > 100:
        raise ValueError("Nome ou e-mail muito longos (máx. 100 caracteres).")

def validar_registro_passagem(registro):
    campos = ['id', 'data', 'id_sensor', 'delta', 'bateria', 'entrada', 'saida']
    for campo in campos:
        if campo not in registro:
            raise ValueError(f"Campo obrigatório ausente: {campo}")

