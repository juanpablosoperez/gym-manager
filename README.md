# 🏋️ Gym Manager - Sistema de Gestión para Gimnasios

**Gym Manager** es una aplicación de escritorio desarrollada en **Python** utilizando **Flet** para la interfaz gráfica y **SQLAlchemy** para la gestión de la base de datos MySQL.  
El sistema permite administrar clientes, pagos, rutinas y generar reportes.

---

## 📌 **Tecnologías Utilizadas**
- **Python 3.12+**
- **Flet** → Framework para la interfaz gráfica
- **SQLAlchemy** → ORM para base de datos
- **Alembic** → Migraciones de base de datos
- **MySQL** → Base de datos relacional
- **Pandas, OpenPyXL** → Manejo de archivos Excel
- **Matplotlib, Seaborn** → Visualización de datos
- **Poetry** → Gestión de dependencias
- **Git & GitHub** → Control de versiones

---

## ⚙️ **Requisitos Previos**
Antes de instalar el proyecto, asegúrate de tener:
- **Python 3.12+** [Descargar aquí](https://www.python.org/downloads/)
- **Git** instalado [Descargar aquí](https://git-scm.com/downloads)
- **Poetry** instalado:
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -


**🚀 Instalación**
1️⃣ Clonar el Repositorio
git clone https://github.com/TU_USUARIO/gym-manager.git
cd gym-manager

**2️⃣ Configurar Poetry y Dependencias**
poetry install

**3️⃣ Activar el Entorno Virtual**
poetry shell

**4️⃣ Instalar Dependencias Adicionales**
poetry add flet sqlalchemy alembic pymysql
poetry add pandas openpyxl matplotlib seaborn numpy
poetry add --dev black isort pylint pytest

**📂 Estructura del Proyecto**

gym-manager/
│── gym_manager/        # Módulo principal
│   ├── controllers/    # Lógica de negocio
│   ├── models/         # Modelos de base de datos (SQLAlchemy)
│   ├── views/          # Interfaz gráfica con Flet
│   ├── services/       # Servicios auxiliares (auth, DB, Excel)
│   ├── config.py       # Configuración del sistema
│   ├── main.py         # Punto de entrada de la aplicación
│
│── tests/              # Pruebas unitarias
│── .gitignore          # Archivos ignorados en Git
│── .env                # Variables de entorno (credenciales)
│── poetry.lock         # Dependencias Poetry
│── pyproject.toml      # Configuración de Poetry
│── README.md           # Documentación del proyecto

**🏃 Ejecutar el Proyecto**
python gym_manager/main.py


**🛠 Migraciones con Alembic**

1️⃣ Inicializar Alembic

alembic init alembic

2️⃣ Configurar alembic.ini

Abre el archivo alembic.ini y edita la línea:

sqlalchemy.url = mysql+pymysql://usuario:contraseña@localhost/gym_manager

3️⃣ Crear y Aplicar Migraciones
alembic revision --autogenerate -m "Inicialización de la BD"
alembic upgrade head

**🛠 Uso de Git**
📌 Subir Cambios a GitHub
git add .
git commit -m "Estructura inicial del proyecto"
git push origin main

🆕 Crear y Cambiar de Ramas
git checkout -b nueva-feature

Crear pull request
git push origin rama-a-pushear
