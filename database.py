from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class HistoricoDirecao(db.Model):
    __tablename__ = 'historico_direcao'

    id = db.Column(db.Integer, primary_key=True)
    direcao = db.Column(db.String(20), nullable=False)
    criado_em = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "direcao": self.direcao,
            "criado_em": self.criado_em.isoformat()
        }
