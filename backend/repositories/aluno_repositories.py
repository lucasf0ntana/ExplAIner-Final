from sqlalchemy import text
from models.database import db
from models.model_aluno import Aluno

class AlunoRepository:
    @staticmethod
    def buscar_ranking():
        banco = db.session.get_bind().dialect.name

        if banco == "mysql":
            sql = text("CALL sp_ranking_alunos()")
            resultado = db.session.execute(sql)
            linhas = resultado.mappings().all()
            resultado.close()
            return [dict(linha) for linha in linhas]

        sql_sqlite = text("""
            SELECT Ranking.classificacao, Ranking.pontos, Aluno.nome 
            FROM Ranking
            JOIN Aluno ON Ranking.id_aluno = Aluno.id_aluno
            ORDER BY Ranking.pontos DESC, Ranking.classificacao DESC
        """)

        resultado = db.session.execute(sql_sqlite)
        linhas = resultado.mappings().all()
        resultado.close()

        return [dict(linha) for linha in linhas]
        
        
