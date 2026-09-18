import json
import os

import paho.mqtt.client as mqtt

from database import db, HistoricoDirecao

BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
PORT = int(os.getenv("MQTT_PORT", "1883"))
TOPIC = os.getenv("MQTT_TOPIC", "senai510/mhss/mov")
DIRECOES_VALIDAS = {"FRENTE", "TRAS", "ESQUERDA", "DIREITA", "CENTRO"}
LIMITE_HISTORICO = 500


def init_mqtt(app):
    def on_connect(client, userdata, flags, reason_code, properties=None):
        print(f"Conectado ao broker MQTT; código: {reason_code}")
        client.subscribe(TOPIC)
        print(f"Inscrito no tópico: {TOPIC}")

    def on_message(client, userdata, msg):
        payload_bruto = msg.payload.decode("utf-8", errors="replace").strip()
        print(f"Mensagem recebida em '{msg.topic}': {payload_bruto}")

        try:
            dados = json.loads(payload_bruto)
            dados_normalizados = {str(chave).upper(): valor for chave, valor in dados.items()}
            direcao = str(dados_normalizados.get("MOVIMENTO", "")).strip().upper()
        except json.JSONDecodeError:
            direcao = payload_bruto.upper()
        except AttributeError:
            print(f"Payload inválido, ignorado: {payload_bruto}")
            return

        if direcao not in DIRECOES_VALIDAS:
            print(f"Direção inválida ignorada: {direcao}")
            return

        try:
            with app.app_context():
                novo_registro = HistoricoDirecao(direcao=direcao)
                db.session.add(novo_registro)
                db.session.flush()

                if HistoricoDirecao.query.count() > LIMITE_HISTORICO:
                    removidos = db.session.query(HistoricoDirecao).delete(synchronize_session=False)
                    db.session.commit()
                    print(f"Limite de {LIMITE_HISTORICO} registros atingido; {removidos} registros apagados.")
                    return

                db.session.commit()
                print(f"Salvo no banco: {direcao} (id={novo_registro.id})")
                app.config["PUBLICAR_DIRECAO"](novo_registro.to_dict())
        except Exception as erro:
            db.session.rollback()
            print(f"Erro ao salvar no banco: {erro}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER, PORT, 60)
        client.loop_start()
    except Exception as erro:
        print(f"Aviso de conexão MQTT: {erro}")

    return client
