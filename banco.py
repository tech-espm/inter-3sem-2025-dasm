from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from config import conexao_banco
import logging
import re

logger = logging.getLogger(__name__)

engine = create_engine(conexao_banco)

def listarPessoas():
    try:
        with Session(engine) as sessao:
            pessoas = sessao.execute(text("SELECT id, nome, email FROM pessoa ORDER BY nome"))
            return [dict(id=id, nome=nome, email=email) for id, nome, email in pessoas]
    except SQLAlchemyError as e:
        logger.error(f"Erro ao listar pessoas: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao listar pessoas: {e}")
        raise

def obterPessoa(id):
    try:
        with Session(engine) as sessao:
            parametros = {'id': id}
            pessoa = sessao.execute(text("SELECT id, nome, email FROM pessoa WHERE id = :id"), parametros).first()
            if pessoa:
                return dict(id=pessoa.id, nome=pessoa.nome, email=pessoa.email)
            return None
    except SQLAlchemyError as e:
        logger.error(f"Erro ao obter pessoa: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao obter pessoa: {e}")
        raise

def criarPessoa(nome, email):
    try:
        validar_pessoa(nome, email)
        with Session(engine) as sessao, sessao.begin():
            pessoa = {'nome': nome, 'email': email}
            sessao.execute(text("INSERT INTO pessoa (nome, email) VALUES (:nome, :email)"), pessoa)
    except ValueError as ve:
        logger.warning(f"Validação falhou ao criar pessoa: {ve}")
        raise
    except IntegrityError as e:
        logger.error(f"Erro de integridade ao criar pessoa: {e}")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Erro ao criar pessoa: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao criar pessoa: {e}")
        raise

def obterIdMaximo(tabela):
    try:
        with Session(engine) as sessao:
            registro = sessao.execute(text(f"SELECT MAX(id) id FROM {tabela}")).first()
            return registro.id if registro and registro.id is not None else 0
    except SQLAlchemyError as e:
        logger.error(f"Erro ao obter id máximo da tabela {tabela}: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao obter id máximo da tabela {tabela}: {e}")
        raise

def inserirDados(registros):
    try:
        with Session(engine) as sessao, sessao.begin():
            for registro in registros:
                validar_registro_passagem(registro)
                sessao.execute(
                    text("INSERT INTO passagem (id, data, id_sensor, delta, bateria, entrada, saida) VALUES (:id, :data, :id_sensor, :delta, :bateria, :entrada, :saida)"),
                    registro
                )
    except ValueError as ve:
        logger.warning(f"Validação falhou ao inserir dados de passagem: {ve}")
        raise
    except IntegrityError as e:
        logger.error(f"Erro de integridade ao inserir dados: {e}")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Erro ao inserir dados: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao inserir dados: {e}")
        raise

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
            return [
                {"dia_semana": dia_semana, "hora": hora, "total": total}
                for dia_semana, hora, total in registros
            ]
    except SQLAlchemyError as e:
        logger.error(f"Erro ao listar consolidado da semana: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao listar consolidado da semana: {e}")
        raise

def listarConsolidadoMensalDiaSemana(data_inicial, data_final, dia_semana):
    try:
        with Session(engine) as sessao:
            parametros = {
                'data_inicial': data_inicial + ' 00:00:00',
                'data_final': data_final + ' 23:59:59',
                'dia_semana': dia_semana
            }
            registros = sessao.execute(text("""
                select date_format(date(data), '%Y-%m-%d') diaISO, date_format(date(data), '%d/%m/%Y') dia, extract(hour from data) hora, cast(sum(entrada + saida) as signed) total
                from passagem
                where data between :data_inicial and :data_final
                and dayofweek(data) = :dia_semana
                and id_sensor = 2
                group by diaISO, dia, hora
				order by diaISO, hora;
            """), parametros)
            return [
                { "dia": dia, "hora": hora, "total": total}
                for diaISO, dia, hora, total in registros
            ]
    except SQLAlchemyError as e:
        logger.error(f"Erro ao listar consolidado mensal por dia da semana: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao listar consolidado mensal por dia da semana: {e}")
        raise

def listarConsolidadoMensalPresenca(data_inicial, data_final):
    try:
        with Session(engine) as sessao:
            parametros = {
                'data_inicial': data_inicial + ' 00:00:00',
                'data_final': data_final + ' 23:59:59'
            }
            registros = sessao.execute(text("""
                select date_format(date(data), '%Y-%m-%d') diaISO, date_format(date(data), '%d/%m') dia, extract(hour from data) hora, cast(sum(entrada) as signed) total_entrada, cast(sum(saida) as signed) total_saida
                from passagem
                where data between :data_inicial and :data_final
                and id_sensor = 2
                group by diaISO, dia, hora
                order by diaISO, hora;
            """), parametros)
            return [
                {"diaISO": diaISO, "dia": dia, "hora": hora, "total_entrada": total_entrada, "total_saida": total_saida}
                for diaISO, dia, hora, total_entrada, total_saida in registros
            ]
    except SQLAlchemyError as e:
        logger.error(f"Erro ao listar consolidado mensal de presença: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao listar consolidado mensal de presença: {e}")
        raise

def listarContratantes():
    try:
        with Session(engine) as sessao:
            resultado = sessao.execute(text("""
                SELECT id, nome, email, empresa FROM contratante ORDER BY nome """))
            return [
                {'id': id, 'nome': nome, 'email': email, 'empresa': empresa}
                for id, nome, email, empresa in resultado
            ]
    except SQLAlchemyError as e:
        logger.error(f"Erro ao listar contratantes: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao listar contratantes: {e}")
        raise

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
    except SQLAlchemyError as e:
        logger.error(f"Erro ao obter contratante: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao obter contratante: {e}")
        raise

def criarContratante(nome, email, empresa, senha):
    try:
        with Session(engine) as sessao, sessao.begin():
            sessao.execute(text("""
                INSERT INTO contratante(nome, email, empresa, senha)
                VALUES (:nome, :email, :empresa, :senha)"""),
                {'nome': nome, 'email': email, 'empresa': empresa, 'senha': senha})
    except IntegrityError as e:
        logger.error(f"Erro de integridade ao criar contratante: {e}")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Erro ao criar contratante: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao criar contratante: {e}")
        raise

def atualizarContratante(id, nome, email, empresa):
    try:
        with Session(engine) as sessao, sessao.begin():
            sessao.execute(text("""
                UPDATE contratante
                SET nome = :nome, email = :email, empresa = :empresa
                WHERE id = :id"""),
                {'id': id, 'nome': nome, 'email': email, 'empresa': empresa})
    except IntegrityError as e:
        logger.error(f"Erro de integridade ao atualizar contratante: {e}")
        raise
    except SQLAlchemyError as e:
        logger.error(f"Erro ao atualizar contratante: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar contratante: {e}")
        raise

def deletarContratante(id):
    try:
        with Session(engine) as sessao, sessao.begin():
            sessao.execute(text(""" DELETE FROM contratante WHERE id = :id """), {'id': id})
    except SQLAlchemyError as e:
        logger.error(f"Erro ao deletar contratante: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao deletar contratante: {e}")
        raise

def obterContratantePorEmail(email):
    try:
        with Session(engine) as sessao:
            resultado = sessao.execute(
                text("SELECT id, nome, email, empresa, senha FROM contratante WHERE email = :email"),
                {'email': email}
            ).first()
            if resultado:
                return {
                    'id': resultado.id,
                    'nome': resultado.nome,
                    'email': resultado.email,
                    'empresa': resultado.empresa,
                    'senha': resultado.senha
                }
            return None
    except SQLAlchemyError as e:
        logger.error(f"Erro ao obter contratante por email: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao obter contratante por email: {e}")
        raise

def validar_email(email):
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