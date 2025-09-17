# test_fastapi_db.py
from src.core.db import get_db
from src.models import Warehouse  # Ajusta según tu modelo

def test_db_in_fastapi_context():
    try:
        db_gen = get_db()
        db = next(db_gen)
        
        print("🔍 Probando consulta en contexto FastAPI...")
        rows = db.query(Warehouse).all()
        print(f"✅ Consulta exitosa: {len(rows)} registros")
        
        # Cerrar la sesión manualmente
        next(db_gen, None)
        
    except Exception as e:
        print(f"❌ Error en contexto FastAPI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db_in_fastapi_context()