# 🏋️ Gym Manager - Sistema de Gestión para Gimnasios

**Gym Manager** es una aplicación de escritorio desarrollada en **Python** utilizando **Flet** para la interfaz gráfica y **SQLAlchemy** para la gestión de la base de datos MySQL.  
El sistema permite administrar clientes, pagos, rutinas y generar reportes.

## 🎯 **Características Principales**
- 👥 **Gestión de Miembros** - Registro completo de clientes
- 💰 **Sistema de Pagos** - Múltiples métodos de pago y facturación
- 🏃 **Rutinas de Entrenamiento** - Creación y asignación de rutinas
- 📊 **Reportes y Estadísticas** - Dashboard interactivo con gráficos
- 🔒 **Gestión de Usuarios** - Sistema de roles y permisos
- 💾 **Backups Automáticos** - Respaldo y restauración de datos
- 📱 **Interfaz Moderna** - UI intuitiva y responsive

---

## 📌 **Tecnologías Utilizadas**
- **Python 3.12+**
- **Flet** → Framework para la interfaz gráfica
- **SQLAlchemy** → ORM para base de datos
- **Alembic** → Migraciones de base de datos
- **MySQL** → Base de datos relacional
- **Pandas, OpenPyXL** → Manejo de archivos Excel
- **Matplotlib, Seaborn, Plotly** → Visualización de datos
- **ReportLab** → Generación de PDFs
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

---

## 📁 **Estructura del Proyecto**

```
gym_manager/
├── 📁 assets/                  ← Recursos (iconos, logos)
├── 📁 components/              ← Componentes reutilizables
├── 📁 controllers/             ← Lógica de negocio
├── 📁 database/                ← Configuración de BD
├── 📁 models/                  ← Modelos de datos
├── 📁 services/                ← Servicios (backup, auth, etc.)
├── 📁 utils/                   ← Utilidades (paginación, navegación)
├── 📁 views/                   ← Vistas de la interfaz
├── 📁 pack/                    ← Archivos de distribución
│   ├── 📁 files/               ← Instaladores y configuración
│   └── 📄 installer.iss        ← Script de Inno Setup
├── 📄 main.py                   ← Punto de entrada
└── 📄 config.py                ← Configuración principal

# Scripts de Build
├── 📄 build_all_versions.bat   ← Genera todas las versiones
├── 📄 build_complete.bat       ← Genera versión instalable
├── 📄 create_portable_version.bat ← Genera versión portable
├── 📄 test_portable.bat        ← Prueba la versión portable
└── 📄 Gym_Manager_Optimized.spec ← Configuración PyInstaller

# Documentación
├── 📄 README.md                ← Este archivo
├── 📄 README_CLIENTE.md        ← Guía para clientes
└── 📄 BUILD_INSTRUCTIONS.md    ← Instrucciones detalladas
```

---

## 🎯 **Resumen de Funcionalidades**

### **👥 Gestión de Miembros**
- Registro completo con fotos y datos personales
- Historial de membresías y pagos
- Búsqueda y filtrado avanzado
- Exportación a Excel/PDF

### **💰 Sistema de Pagos**
- Múltiples métodos de pago
- Facturación automática
- Reportes de ingresos
- Renovaciones automáticas

### **🏃 Rutinas de Entrenamiento**
- Creación de rutinas personalizadas
- Asignación a miembros
- Seguimiento de progreso
- Documentos adjuntos

### **📊 Reportes y Estadísticas**
- Dashboard interactivo
- Gráficos con Plotly
- Reportes personalizables
- Exportación múltiple

### **🔒 Gestión de Usuarios**
- Sistema de roles (admin, usuario)
- Autenticación segura
- Permisos granulares
- Auditoría de acciones

### **💾 Sistema de Backups**
- Backups automáticos programados
- Restauración con un clic
- Compresión y almacenamiento
- Verificación de integridad

---

## 🚀 **Inicio Rápido**

### **Para Desarrolladores:**
```bash
# 1. Clonar repositorio
git clone https://github.com/TU_USUARIO/gym-manager.git
cd gym-manager

# 2. Instalar dependencias
poetry install

# 3. Activar entorno
poetry shell

# 4. Ejecutar aplicación
python gym_manager/main.py
```

### **Para Distribución:**
```bash
# Generar todas las versiones
build_all_versions.bat

# O solo la portable (recomendada)
create_portable_version.bat
```

### **Para Clientes Finales:**
1. **Descargar** `Gym Manager_Portable_1.0.0.zip`
2. **Descomprimir** en cualquier carpeta
3. **Ejecutar** `Iniciar_Gym_Manager.bat` como administrador
4. **¡Listo!** Todo se configura automáticamente

---

## 📞 **Soporte y Contacto**

### **🐛 Reportar Problemas**
- **GitHub Issues:** [Crear un issue](https://github.com/TU_USUARIO/gym-manager/issues)
- **Email:** soporte@gymmanager.com
- **Documentación:** Revisar README_CLIENTE.md

### **💡 Solicitar Funcionalidades**
- **GitHub Discussions:** [Discusiones](https://github.com/TU_USUARIO/gym-manager/discussions)
- **Email:** desarrollo@gymmanager.com

### **📚 Documentación Adicional**
- **README_CLIENTE.md** - Guía completa para usuarios finales
- **BUILD_INSTRUCTIONS.md** - Instrucciones detalladas de build
- **docs/** - Documentación técnica (si está disponible)

---

## 📄 **Licencia y Créditos**

### **📜 Licencia**
Este proyecto está bajo la licencia **MIT**. Ver el archivo `LICENSE` para más detalles.

### **👥 Desarrolladores**
- **Desarrollador Principal:** [Tu Nombre]
- **Contribuidores:** [Lista de contribuidores]

### **🙏 Agradecimientos**
- **Flet** - Framework de interfaz gráfica
- **SQLAlchemy** - ORM para Python
- **MySQL** - Base de datos relacional
- **Plotly** - Visualización de datos
- **Poetry** - Gestión de dependencias

---

## 🔄 **Historial de Versiones**

### **v1.0.0** (Actual)
- ✅ Sistema completo de gestión de gimnasios
- ✅ Interfaz moderna con Flet
- ✅ Sistema de backups automáticos
- ✅ Reportes y estadísticas avanzadas
- ✅ Versión portable y instalable
- ✅ Configuración automática de MySQL
- ✅ Documentación completa

### **Próximas Versiones**
- 🔄 **v1.1.0** - Mejoras en reportes
- 🔄 **v1.2.0** - Integración con sistemas de pago
- 🔄 **v2.0.0** - Versión web/móvil

---

## 🎉 **¡Gracias por usar Gym Manager!**

**Gym Manager** es una solución completa y profesional para la gestión de gimnasios. 
Con su interfaz moderna, funcionalidades avanzadas y facilidad de uso, 
te ayudará a administrar tu negocio de manera eficiente.

### **⭐ Si te gusta el proyecto:**
- Dale una estrella en GitHub
- Comparte con otros gimnasios
- Contribuye al desarrollo
- Reporta bugs o sugiere mejoras

### **🚀 ¡Comienza hoy mismo!**
Descarga la versión portable, descomprime y ejecuta. 
¡En menos de 5 minutos tendrás tu sistema de gestión funcionando!

---

**Desarrollado con ❤️ para la comunidad fitness** 🏋️‍♂️

El proyecto incluye un sistema completo de build que genera **dos versiones** listas para distribución:

#### **🎯 Versión Portable (RECOMENDADA)**
- ✅ **No requiere instalación** - Solo ejecutar
- ✅ **No modifica el registro** de Windows
- ✅ **Fácil de transportar** - Copiar carpeta completa
- ✅ **Fácil de desinstalar** - Solo eliminar carpeta
- ✅ **Configuración automática** de MySQL
- ✅ **Funciona en cualquier PC** sin configuración previa

#### **🎯 Versión Instalable**
- ✅ Instalación tradicional en Program Files
- ✅ Acceso directo en el escritorio
- ✅ Desinstalador incluido
- ✅ Configuración automática de MySQL

### **🔧 Scripts de Build Disponibles**

#### **1. Build Completo (TODAS LAS VERSIONES)**
```bash
build_all_versions.bat
```
**Genera:**
- `Gym Manager_1.0.0_Complete.zip` (versión instalable)
- `Gym Manager_Portable_1.0.0.zip` (versión portable)

#### **2. Build Solo Instalable**
```bash
build_complete.bat
```
**Genera:**
- Ejecutable con PyInstaller o Flet
- ZIP con instaladores y configuración

#### **3. Build Solo Portable**
```bash
create_portable_version.bat
```
**Genera:**
- `Gym Manager_Portable_1.0.0.zip`
- Versión completamente portable

### **📁 Estructura de Archivos Generados**

#### **Versión Instalable:**
```
Gym Manager_1.0.0_Complete/
├── 🚀 Gym Manager.exe          ← Aplicación principal
├── 📁 install/                 ← Archivos de instalación
│   ├── 🗄️ MySQLInstallerConsole.exe
│   ├── 📄 schema.sql
│   ├── ⚙️ setup.bat
│   └── 📁 assets/
├── 📁 assets/                  ← Recursos adicionales
├── 🔧 GymManagerSetup.exe      ← Instalador completo (si está disponible)
└── 📖 README_INSTALACION.txt   ← Instrucciones técnicas
```

#### **Versión Portable:**
```
Gym Manager_Portable_1.0.0/
├── 🚀 Iniciar_Gym_Manager.bat  ← EJECUTAR ESTE
├── 📁 app/                     ← Aplicación completa
│   ├── 🚀 Gym Manager.exe
│   ├── 📁 _internal/           ← Todas las dependencias Python
│   └── 📁 assets/
├── 📁 data/                    ← Configuración
│   └── 📄 schema.sql
├── 📁 mysql/                   ← Instalador MySQL
│   └── 🗄️ MySQLInstallerConsole.exe
└── 📖 README_PORTABLE.txt      ← Instrucciones de la versión portable
```

### **🎯 Instrucciones para el Cliente Final**

#### **Opción 1: Versión Portable (MÁS RECOMENDADA)**
1. **Descomprimir** `Gym Manager_Portable_1.0.0.zip`
2. **Ejecutar como administrador** `Iniciar_Gym_Manager.bat`
3. **¡Listo!** Todo se configura automáticamente

#### **Opción 2: Versión Instalable**
1. **Descomprimir** `Gym Manager_1.0.0_Complete.zip`
2. **Ejecutar como administrador** `install\setup.bat`
3. **¡Listo!** Se instala en Program Files

### **🔧 Comandos de Build Manuales**

#### **Con Flet (Recomendado):**
```bash
# Generación básica
flet pack gym_manager\main.py --name "Gym Manager" --icon gym_manager\assets\app.ico --add-data "gym_manager\assets;assets"

# Con Poetry
poetry run flet pack gym_manager\main.py --name "Gym Manager" --icon gym_manager\assets\app.ico --add-data "gym_manager\assets;assets" --hidden-import gym_manager.views.member_view --hidden-import gym_manager.views.backup_view --hidden-import gym_manager.views.statistics_view --hidden-import gym_manager.controllers.statistics_controller --hidden-import gym_manager.views.payment_view --hidden-import gym_manager.views.routine_view --hidden-import gym_manager.views.user_view --hidden-import gym_manager.views.payment_method_view --hidden-import gym_manager.services.backup_service --hidden-import gym_manager.services.restore_service
```

#### **Con PyInstaller:**
```bash
# Usando el archivo .spec optimizado
py -m PyInstaller Gym_Manager_Optimized.spec --noconfirm
```

### **📋 Requisitos para Build**

#### **Herramientas Necesarias:**
- **Python 3.12+** con Poetry
- **Flet** (se instala automáticamente)
- **PyInstaller** (se instala automáticamente)
- **Inno Setup** (opcional, para instalador)

#### **Archivos de Instalación:**
- `gym_manager/pack/files/MySQLInstallerConsole.exe`
- `gym_manager/pack/files/schema.sql`
- `gym_manager/pack/files/setup.bat`

### **🛠️ Características del Sistema de Build**

#### **Detección Automática:**
- ✅ **Detecta Flet** y lo instala si no está presente
- ✅ **Usa PyInstaller como respaldo** si Flet falla
- ✅ **Verifica archivos** antes de proceder
- ✅ **Múltiples fallbacks** si algo falla

#### **Configuración Inteligente:**
- ✅ **Instalación automática de MySQL** con configuración completa
- ✅ **Creación automática de base de datos**
- ✅ **Configuración de archivos .env**
- ✅ **Generación de accesos directos**

#### **Manejo de Errores:**
- ✅ **Mensajes informativos** en cada paso
- ✅ **Verificación de permisos** de administrador
- ✅ **Detección de MySQL** en múltiples ubicaciones
- ✅ **Validación de archivos** generados

### **📞 Soporte y Troubleshooting**

#### **Problemas Comunes:**
1. **"Flet no encontrado"** → Se instala automáticamente
2. **"PyInstaller no encontrado"** → Se instala automáticamente
3. **"MySQL no se instala"** → Verificar permisos de administrador
4. **"No se puede crear el ZIP"** → Verificar permisos de escritura

#### **Solución de Problemas:**
- Ejecutar scripts como **administrador**
- Verificar que **todos los archivos** estén presentes
- Revisar **logs de error** en la consola
- Usar **versión portable** si hay problemas de instalación

---

## 🏃 **Ejecutar el Proyecto (Desarrollo)**
