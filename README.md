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


**4️⃣ Ejecutar la App con Poetry**
Ahora puedes ejecutar la aplicación con:

Modo Desarrollo:
poetry run dev

Modo Producción:
poetry run prod

Correr Alembic con Poetry:
poetry run alembic upgrade head

3️⃣ Crear migraciones:
poetry run alembic revision --autogenerate -m "Migración inicial"


📌 1️⃣0️⃣ Resumen de Comandos
Acción	                        Comando
Instalar Alembic	            poetry add alembic
Inicializar Alembic	            poetry run alembic init alembic
Crear una migración	            poetry run alembic revision --autogenerate -m "Descripción"
Aplicar migraciones	            poetry run alembic upgrade head
Ver historial de migraciones	poetry run alembic history
Ver estado actual	            poetry run alembic current

# Ejecutable (con gráficos nativos de Flet)
flet pack gym_manager\main.py --name "Gym Manager" --icon gym_manager\assets\app.ico --add-data "gym_manager\assets;assets" --hidden-import gym_manager.views.member_view --hidden-import gym_manager.views.backup_view --hidden-import gym_manager.views.statistics_view --hidden-import gym_manager.controllers.statistics_controller --hidden-import gym_manager.views.payment_view --hidden-import gym_manager.views.routine_view --hidden-import gym_manager.views.user_view --hidden-import gym_manager.views.payment_method_view --hidden-import gym_manager.services.backup_service --hidden-import gym_manager.services.restore_service

# GENERACION DE EJECUTABLE CON TODAS LAS DEPENDENCIAS con poetry (con gráficos nativos de Flet)
poetry run flet pack gym_manager\main.py --name "Gym Manager" --icon gym_manager\assets\app.ico --add-data "gym_manager\assets;assets" --hidden-import gym_manager.views.member_view --hidden-import gym_manager.views.backup_view --hidden-import gym_manager.views.statistics_view --hidden-import gym_manager.controllers.statistics_controller --hidden-import gym_manager.views.payment_view --hidden-import gym_manager.views.routine_view --hidden-import gym_manager.views.user_view --hidden-import gym_manager.views.payment_method_view --hidden-import gym_manager.services.backup_service --hidden-import gym_manager.services.restore_service

# Comando anterior con Plotly (ya no necesario)
# flet pack gym_manager\main.py --name "Gym Manager" --icon gym_manager\assets\app.ico --add-data "gym_manager\assets;assets" --hidden-import gym_manager.views.member_view --hidden-import gym_manager.views.backup_view --hidden-import gym_manager.views.statistics_view --hidden-import gym_manager.controllers.statistics_controller --hidden-import gym_manager.views.payment_view --hidden-import gym_manager.views.routine_view --hidden-import gym_manager.views.user_view --hidden-import gym_manager.views.payment_method_view --hidden-import gym_manager.services.backup_service --hidden-import gym_manager.services.restore_service --hidden-import plotly --hidden-import flet.plotly_chart --hidden-import kaleido --hidden-import plotly.graph_objs --hidden-import plotly.graph_objects --hidden-import plotly.express --hidden-import plotly.io --hidden-import plotly.offline --hidden-import plotly.utils --hidden-import plotly.colors --hidden-import plotly.figure_factory --hidden-import plotly.data --hidden-import plotly.validators --hidden-import plotly.subplots --hidden-import plotly.tools --hidden-import plotly.dashboard_objs --hidden-import plotly.widgets --hidden-import _plotly_utils --hidden-import _plotly_future_ --hidden-import tenacity --hidden-import retrying --hidden-import six --hidden-import packaging --hidden-import packaging.version --hidden-import packaging.specifiers --hidden-import packaging.requirements