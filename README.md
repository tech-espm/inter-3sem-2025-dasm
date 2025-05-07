# Projeto Interdisciplinar III - Sistemas de Informação ESPM

<p align="center">
    <a href="https://www.espm.br/cursos-de-graduacao/sistemas-de-informacao/"><img src="https://raw.githubusercontent.com/tech-espm/misc-template/main/logo.png" alt="Sistemas de Informação ESPM" style="width: 375px;"/></a>
</p>

# Data Analysis for Scheduled Maintenance

### 2025-01

## Integrantes
- [Bianca Fagundes](https://github.com/araujozb)
- [Gustavo Dutra](https://github.com/snowdutra)
- [Luzivania Bonfim](https://github.com/bonfim1)
- [Maria Gabriela Vieira](https://github.com/mgabriel4)
- [Mateus Colmeal](https://github.com/mcolmeal)

## Descrição do Projeto

### Problema a ser resolvido

- Altos custos com manutenção reativa
- Mau aproveitamento de recursos humanos
- Perda de lucro por bloqueios indevidos de espaços

### Solução

A solução proposta pelo projeto está baseada em três grandes pilares:

- Manutenção Programada
    - Histórico de horários de maior fluxo de pessoas
    - Manutenções nos períodos de menor fluxo 
    - Alerta de manutenções antecipadas
- Sensores de Passagem
    - Predição de picos de movimentação
- Checkpoint
    - Os contadores são reiniciados diariamente

## Configuração do Projeto

Para executar, deve criar o arquivo `config.py` da seguinte forma:

```python
host = '0.0.0.0'
port = 3000
conexao_banco = 'mysql+mysqlconnector://usuario:senha@host/banco'
url_api = 'https://site.com'
```

Todos os comandos abaixo assumem que o terminal esteja com o diretório atual na raiz do projeto.

## Criação e Ativação do venv

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Execução

```
.venv\Scripts\activate
python app.py
```

## Mais Informações

https://flask.palletsprojects.com/en/3.0.x/quickstart/
https://flask.palletsprojects.com/en/3.0.x/tutorial/templates/

# Licença

Este projeto é licenciado sob a [MIT License](https://github.com/tech-espm/inter-3sem-2025-toilet-view/blob/main/LICENSE).

<p align="right">
    <a href="https://www.espm.br/cursos-de-graduacao/sistemas-de-informacao/"><img src="https://raw.githubusercontent.com/tech-espm/misc-template/main/logo-si-512.png" alt="Sistemas de Informação ESPM" style="width: 375px;"/></a>
</p>
