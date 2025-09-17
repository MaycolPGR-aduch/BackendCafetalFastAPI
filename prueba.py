import pyodbc

# Prueba la conexión directa
try:
    conn = pyodbc.connect(
        r'DRIVER={ODBC Driver 18 for SQL Server};'
        r'SERVER=DESKTOP-4L8G0LG\SQLEXPRESS;'
        r'DATABASE=Cafetal;'
        r'Trusted_Connection=yes;'
        r'TrustServerCertificate=yes;'
        r'Encrypt=no;'
    )
    print("✅ Conexión exitosa!")
    conn.close()
except Exception as e:
    print(f"❌ Error de conexión: {e}")