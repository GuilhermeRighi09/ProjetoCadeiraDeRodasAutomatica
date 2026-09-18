import pytest

from App import create_app
from database import db, HistoricoDirecao


@pytest.fixture
def app():
    app_teste = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"},
        iniciar_mqtt=False,
    )
    yield app_teste
    with app_teste.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_rota_index_sucesso(client):
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert b"Painel Cadeira de Rodas IoT" in resposta.data


def test_rota_status_sucesso(client):
    resposta = client.get("/api/status")
    assert resposta.status_code == 200
    assert resposta.json["status"] == "API da Cadeira de Rodas ativa"


def test_obter_historico_retorna_lista(client):
    resposta = client.get("/api/historico")
    assert resposta.status_code == 200
    assert resposta.json == []


def test_rota_inexistente_retorna_404(client):
    assert client.get("/api/rota_invalida").status_code == 404


@pytest.mark.parametrize("direcao_input", ["FRENTE", "TRAS", "ESQUERDA", "DIREITA"])
def test_salvamento_direcoes_parametrizado(app, direcao_input):
    with app.app_context():
        db.session.add(HistoricoDirecao(direcao=direcao_input))
        db.session.commit()

        registro = HistoricoDirecao.query.filter_by(direcao=direcao_input).first()
        assert registro is not None
        assert registro.direcao == direcao_input
