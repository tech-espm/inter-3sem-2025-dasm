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
	# O with do Python é similar ao using do C#, ou o try with resources do Java.
	# Ele serve para limitar o escopo/vida do objeto automaticamente, garantindo
	# que recursos, como uma conexão com o banco, não sejam desperdiçados!
	with Session(engine) as sessao:
		pessoas = sessao.execute(text("SELECT id, nome, email FROM pessoa ORDER BY nome"))

		# Como cada registro retornado é uma tupla ordenada, é possível
		# utilizar a forma de enumeração de tuplas:
		for (id, nome, email) in pessoas:
			print(f'\nid: {id} / nome: {nome} / email: {email}')

		# Ou, se preferir, é possível retornar cada tupla, o que fica mais parecido
		# com outras linguagens de programação:
		#for pessoa in pessoas:
		#	print(f'\nid: {pessoa.id} / nome: {pessoa.nome} / email: {pessoa.email}')

def obterPessoa(id):
	with Session(engine) as sessao:
		parametros = {
			'id': id
		}

		# Mais informações sobre o método execute e sobre o resultado que ele retorna:
		# https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.execute
		# https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.Result
		pessoa = sessao.execute(text("SELECT id, nome, email FROM pessoa WHERE id = :id"), parametros).first()

		if pessoa == None:
			print('Pessoa não encontrada!')
		else:
			print(f'\nid: {pessoa.id} / nome: {pessoa.nome} / email: {pessoa.email}')

def criarPessoa(nome, email):
	# É importante utilizar o método begin() para que a sessão seja comitada
	# automaticamente ao final, caso não ocorra uma exceção!
	# Isso não foi necessário nos outros exemplos porque nenhum dado estava sendo
	# alterado lá! Caso alguma exceção ocorra, rollback() será executado automaticamente,
	# e nenhuma alteração será persistida. Para mais informações de como explicitar
	# esse processo de commit() e rollback():
	# https://docs.sqlalchemy.org/en/14/orm/session_basics.html#framing-out-a-begin-commit-rollback-block
	with Session(engine) as sessao, sessao.begin():
		pessoa = {
			'nome': nome,
			'email': email
		}

		sessao.execute(text("INSERT INTO pessoa (nome, email) VALUES (:nome, :email)"), pessoa)

		# Para inserir, ou atualizar, vários registros ao mesmo tempo, a forma mais rápida
		# é passar uma lista como segundo parâmetro:
		# lista = [ ... ]
		# sessao.execute(text("INSERT INTO pessoa (nome, email) VALUES (:nome, :email)"), lista)

# Para mais informações:
# https://docs.sqlalchemy.org/en/14/tutorial/dbapi_transactions.html

def obterIdMaximo(tabela):
	with Session(engine) as sessao:
		registro = sessao.execute(text(f"SELECT MAX(id) id FROM {tabela}")).first()

		if registro == None or registro.id == None:
			return 0
		else:
			return registro.id

def inserirDados(registros):
	with Session(engine) as sessao, sessao.begin():
		for registro in registros:
			sessao.execute(text("INSERT INTO passagem (id, data, id_sensor, delta, bateria, entrada, saida) VALUES (:id, :data, :id_sensor, :delta, :bateria, :entrada, :saida)"), registro)

def listarConsolidadoSemana(data_inicial, data_final):
	with Session(engine) as sessao:
		parametros = {
			'data_inicial': data_inicial + ' 00:00:00',
			'data_final': data_final + ' 23:59:59'
		}

		# Mais informações sobre o método execute e sobre o resultado que ele retorna:
		# https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.execute
		# https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.Result
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

def listarConsolidadoMensalDiaSemana(data_inicial, data_final, dia_semana):
	with Session(engine) as sessao:
		parametros = {
			'data_inicial': data_inicial + ' 00:00:00',
			'data_final': data_final + ' 23:59:59',
			'dia_semana': dia_semana
		}

		# Mais informações sobre o método execute e sobre o resultado que ele retorna:
		# https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.execute
		# https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.Result
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

def listarConsolidadoMensalPresenca(data_inicial, data_final):
	with Session(engine) as sessao:
		parametros = {
			'data_inicial': data_inicial + ' 00:00:00',
			'data_final': data_final + ' 23:59:59'
		}

		# Mais informações sobre o método execute e sobre o resultado que ele retorna:
		# https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.execute
		# https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.Result
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

# ------------------------------
#   CRUD NÃO - CONTRATANTES
#-------------------------------

def listarContratantes():
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

def obterContratante(id):
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

def criarContratante(nome, email, empresa, senha):
	with Session(engine) as sessao, sessao.begin():
		sessao.execute(text("""
            INSERT INTO contratante(nome, email, empresa, senha)
            VALUES (:nome, :email, :empresa, :senha)"""),
			{'nome': nome, 'email': email, 'empresa': empresa, 'senha': senha})
  
def atualizarContratante(id, nome, email, empresa):
	with Session(engine) as sessao, sessao.begin():
		sessao.execute(text("""
			UPDATE contratante
			SET nome = :nome, email = :email, empresa = :empresa
			WHERE id = :id"""),
			{'id': id, 'nome': nome, 'email': email, 'empresa': empresa})
  
def deletarContratante(id):
    with Session(engine) as sessao, sessao.begin():
        sessao.execute(text(""" DELETE FROM contratante WHERE id = :id """), {'id': id})

        