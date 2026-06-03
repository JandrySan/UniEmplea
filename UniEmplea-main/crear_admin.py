from database.mongo_connection import MongoDB
from utils.seguridad import hash_password

db = MongoDB().db

admin = {
    "nombre": "Administrador General",
    "correo": "admin@uniemplea.com",
    "password": hash_password("admin123"),
    "rol": "administrador",
    "activo": True
}

db.usuarios.insert_one(admin)
print("✅ Administrador creado correctamente")
