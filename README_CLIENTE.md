# 🏋️ Gym Manager - Guía de Instalación para Clientes

## 🎯 **¿Qué es Gym Manager?**

**Gym Manager** es una aplicación de escritorio profesional para la gestión completa de gimnasios. Permite administrar:

- 👥 **Miembros y clientes**
- 💰 **Pagos y facturación**
- 🏃 **Rutinas de entrenamiento**
- 📊 **Estadísticas y reportes**
- 🔒 **Usuarios y permisos**
- 💾 **Backups automáticos**

---

## 📦 **Contenido del Paquete**

Al descomprimir el archivo ZIP, encontrarás:

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

---

## 🚀 **Métodos de Instalación**

### **🎯 Opción 1: Instalación Automática (RECOMENDADA)**

**Para usuarios que quieren la instalación más simple:**

1. **Hacer doble clic en `GymManagerSetup.exe`**
2. **Seguir el asistente de instalación**
3. **¡Listo! Todo se instala automáticamente**

**Ventajas:**
- ✅ Instalación completamente automática
- ✅ MySQL se instala y configura solo
- ✅ Base de datos se crea automáticamente
- ✅ Acceso directo en el escritorio
- ✅ Desinstalador incluido

---

### **⚙️ Opción 2: Instalación Semi-Automática**

**Para usuarios que prefieren más control:**

1. **Ejecutar `install\setup.bat`**
2. **Se instala MySQL automáticamente**
3. **Se configura la base de datos**
4. **¡Listo para usar!**

**Ventajas:**
- ✅ MySQL se instala automáticamente
- ✅ Base de datos se configura sola
- ✅ Más control sobre el proceso
- ✅ Instalación rápida

---

### **🔧 Opción 3: Instalación Manual**

**Para usuarios técnicos o si las opciones anteriores fallan:**

1. **Instalar MySQL 8.4 manualmente**
2. **Ejecutar `Gym Manager.exe`**
3. **Configurar la conexión a la base de datos**

---

## 📋 **Requisitos del Sistema**

### **Sistema Operativo:**
- ✅ **Windows 10** (64 bits)
- ✅ **Windows 11** (64 bits)
- ✅ **Windows Server 2016+** (64 bits)

### **Hardware Mínimo:**
- 💻 **Procesador:** Intel Core i3 o AMD equivalente
- 🧠 **Memoria RAM:** 4 GB
- 💾 **Espacio en disco:** 2 GB libres
- 🌐 **Conexión a internet:** Solo para la instalación inicial

### **Software Requerido:**
- 🗄️ **MySQL 8.4** (se instala automáticamente)
- 🔒 **Permisos de administrador** (solo para la instalación)

---

## 🚀 **Instalación Paso a Paso**

### **Paso 1: Preparación**
1. **Descargar el archivo ZIP**
2. **Descomprimir en una carpeta** (ej: `C:\Gym Manager\`)
3. **Cerrar otras aplicaciones** que puedan interferir

### **Paso 2: Instalación**
1. **Ejecutar como administrador** (clic derecho → "Ejecutar como administrador")
2. **Elegir el método de instalación** preferido
3. **Esperar a que termine** (puede tomar varios minutos)

### **Paso 3: Verificación**
1. **Verificar que aparezca el acceso directo** en el escritorio
2. **Ejecutar la aplicación** para confirmar que funciona
3. **¡Listo para usar!**

---

## 🔧 **Configuración Inicial**

### **Primera Ejecución:**
1. **La aplicación se abrirá automáticamente**
2. **Se creará la base de datos** si no existe
3. **Se configurarán las tablas** necesarias
4. **¡Puedes empezar a usar la aplicación!**

### **Configuración de Usuario:**
1. **Crear usuario administrador** en la primera ejecución
2. **Configurar datos del gimnasio** (nombre, dirección, etc.)
3. **Personalizar configuraciones** según tus necesidades

---

## 📊 **Características Principales**

### **Gestión de Miembros:**
- 📝 Registro completo de clientes
- 📸 Fotos de perfil
- 📱 Información de contacto
- 📅 Historial de membresías

### **Sistema de Pagos:**
- 💳 Múltiples métodos de pago
- 📊 Facturación automática
- 📈 Reportes de ingresos
- 🔄 Renovaciones automáticas

### **Rutinas de Entrenamiento:**
- 🏋️ Crear rutinas personalizadas
- 📋 Asignar ejercicios
- 📊 Seguimiento de progreso
- 📱 Acceso desde móvil

### **Reportes y Estadísticas:**
- 📊 Dashboard interactivo
- 📈 Gráficos de crecimiento
- 📋 Reportes personalizables
- 💾 Exportación a Excel/PDF

---

## 🆘 **Solución de Problemas**

### **Error: "No se puede conectar a la base de datos"**
**Solución:**
1. Verificar que MySQL esté ejecutándose
2. Ejecutar `install\setup.bat` nuevamente
3. Reiniciar la aplicación

### **Error: "Permisos insuficientes"**
**Solución:**
1. Ejecutar como administrador
2. Verificar permisos de usuario
3. Desactivar antivirus temporalmente

### **Error: "Puerto 3306 en uso"**
**Solución:**
1. Verificar que no haya otro MySQL instalado
2. Cambiar puerto en la configuración
3. Contactar soporte técnico

### **La aplicación no se abre**
**Solución:**
1. Verificar requisitos del sistema
2. Reinstalar desde el ZIP
3. Verificar archivos antivirus

---

## 📞 **Soporte Técnico**

### **Antes de Contactar Soporte:**
1. ✅ Verificar requisitos del sistema
2. ✅ Revisar esta guía completa
3. ✅ Intentar reinstalación
4. ✅ Verificar logs de error

### **Información Necesaria:**
- 📋 Versión de Windows
- 💻 Especificaciones del equipo
- 📝 Mensaje de error exacto
- 📸 Captura de pantalla del problema

### **Canales de Soporte:**
- 📧 **Email:** soporte@gymmanager.com
- 📱 **WhatsApp:** +54 9 11 1234-5678
- 🌐 **Web:** www.gymmanager.com/soporte
- 📞 **Teléfono:** +54 11 1234-5678

---

## 🔄 **Actualizaciones**

### **¿Cómo Actualizar?**
1. **Descargar la nueva versión** del ZIP
2. **Hacer backup** de la base de datos actual
3. **Descomprimir en la misma carpeta**
4. **Ejecutar el instalador** de la nueva versión

### **¿Qué se Preserva?**
- ✅ **Base de datos** (clientes, pagos, rutinas)
- ✅ **Configuraciones** personalizadas
- ✅ **Archivos de usuario** (fotos, documentos)
- ✅ **Historial** completo

---

## 📚 **Recursos Adicionales**

### **Manual del Usuario:**
- 📖 **Guía completa** de todas las funciones
- 🎥 **Videos tutoriales** paso a paso
- 📋 **FAQ** (Preguntas frecuentes)
- 🔧 **Tips y trucos** para optimizar el uso

### **Capacitación:**
- 🎓 **Sesiones de entrenamiento** online
- 📚 **Material de estudio** descargable
- 🎯 **Certificaciones** de usuario
- 👥 **Comunidad** de usuarios

---

## 🎉 **¡Felicidades!**

**Has instalado exitosamente Gym Manager, la solución más completa para la gestión de gimnasios.**

### **Próximos Pasos:**
1. 🚀 **Explorar todas las funciones**
2. 📚 **Revisar el manual del usuario**
3. 🎓 **Participar en sesiones de capacitación**
4. 📞 **Contactar soporte** si tienes dudas

### **Recuerda:**
- 💾 **Hacer backups regulares** de la base de datos
- 🔄 **Mantener la aplicación actualizada**
- 📊 **Revisar reportes** regularmente
- 👥 **Capacitar a tu equipo** en el uso del sistema

---

## 📄 **Información Legal**

- **Versión:** 1.0.0
- **Licencia:** Comercial
- **Desarrollador:** Gym Manager Team
- **Soporte:** Incluido por 12 meses
- **Garantía:** 30 días

---

**¡Gracias por elegir Gym Manager para tu gimnasio! 🏋️‍♂️**

**Para más información, visita:** www.gymmanager.com
