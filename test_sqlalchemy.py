# test_sqlalchemy.py
from sqlalchemy import create_engine, text

# Usa la misma URI que está funcionando manualmente
DATABASE_URI = "mssql+pyodbc://@DESKTOP-4L8G0LG\\SQLEXPRESS/Cafetal?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes&Encrypt=no"

try:
    engine = create_engine(DATABASE_URI, echo=True)
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        print("✅ SQLAlchemy conectado exitosamente!")
        print("Resultado:", result.fetchone())
        
except Exception as e:
    print(f"❌ Error en SQLAlchemy: {e}")
    import traceback
    traceback.print_exc()