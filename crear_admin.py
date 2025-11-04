from modelos import Administrador
from repositorios import repo_usuarios

admin = Administrador(
    nombre="Admin General",
    correo="admin@uleam.edu.ec",
    contrasena="admin123",
    cargo="Administrador General",
    permisos="todo"
)

repo_usuarios.insertar(admin)
print("✅ Admin creado con correo admin@uleam.edu.ec y contraseña admin123")
