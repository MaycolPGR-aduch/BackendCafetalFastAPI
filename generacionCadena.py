import urllib.parse
params = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=DESKTOP-4L8G0LG\\SQLEXPRESS;"
    "DATABASE=Cafetal;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
    "Encrypt=no;"
)
print("mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(params))
