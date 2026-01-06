from werkzeug.security import generate_password_hash
from database.mongo_connection import MongoDB

db = MongoDB().db

admin = {
    "nombre": "Administrador General",
    "correo": "admin@uniemplea.com",
    "password": generate_password_hash("admin123"),
    "rol": "administrador",
    "activo": True
}

db.usuarios.insert_one(admin)
print("✅ Administrador creadoooo correctamente")
