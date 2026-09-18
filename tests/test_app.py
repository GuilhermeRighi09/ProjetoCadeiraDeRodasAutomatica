import pytest
from App import app, db
from database import HistoricoDirecao

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


def test_rota_index_sucesso(client):
    resposta = client.get('/')
    assert resposta.status_code == 200
    assert b'Painel Cadeira de Rodas IoT' in resposta.data


def test_rota_status_sucesso(client):
    resposta = client.get('/api/status')
    assert resposta.status_code == 200
    assert resposta.json['status'] == "API da Cadeira de Rodas ativa"


def test_obter_historico_retorna_lista(client):
    resposta = client.get('/api/historico')
    assert resposta.status_code == 200
    assert isinstance(resposta.json, list)


def test_rota_inexistente_retorna_404(client):
    resposta = client.get('/api/rota_invalida')
    assert resposta.status_code == 404


@pytest.mark.parametrize("direcao_input, esperado", [
    ("FRENTE", "FRENTE"),
    ("TRAS", "TRAS"),
    ("ESQUERDA", "ESQUERDA"),
    ("DIREITA", "DIREITA"),
])
def test_salvamento_direcoes_parametrizado(client, direcao_input, esperado):
    with app.app_context():
        novo_registro = HistoricoDirecao(direcao=direcao_input)
        db.session.add(novo_registro)
        db.session.commit()

        registro = HistoricoDirecao.query.filter_by(direcao=esperado).first()
        assert registro is not None
        assert registro.direcao == esperado
