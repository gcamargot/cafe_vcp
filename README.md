# Café System

Sistema de gestión integral para cafeterías que permite el manejo de mesas, órdenes, cocina y pagos.

## 🚀 Características

### Backend
- Sistema de autenticación con roles (admin/cajero/cocinero)
- Gestión de mesas y estados
- Sistema de órdenes y comandas
- Panel de cocina con cola de órdenes
- Control de inventario básico
- Integración con MercadoPago (próximamente)
- API REST documentada con OpenAPI

### Frontend (En desarrollo)
- Interfaz web responsive
- Aplicación de escritorio con Electron
- Panel de administración
- Vista de cocina en tiempo real
- Interfaz de punto de venta
- Modo offline (próximamente)

## 🛠 Tecnologías

### Backend
- **Python 3.10+**
- **FastAPI** - Framework web
- **SQLAlchemy** - ORM
- **PostgreSQL** - Base de datos
- **Alembic** - Migraciones
- **JWT** - Autenticación
- **Pytest** - Testing

### Frontend
- **React** - Librería UI
- **TypeScript** - Lenguaje
- **Vite** - Build tool
- **TanStack Query** - Data fetching
- **Zustand** - Estado global
- **TailwindCSS** - Estilos
- **Electron** - Aplicación de escritorio

## 📋 Requisitos del Sistema

### Backend
- Python 3.10+
- PostgreSQL 14+
- Entorno virtual Python

### Frontend
- Node.js 16+
- npm 8+

## 🔧 Instalación

### Backend
```bash
# Clonar el repositorio
git clone [url-del-repositorio]

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Ejecutar migraciones
alembic upgrade head

# Iniciar servidor
uvicorn app.main:app --reload
```

### Frontend
```bash
# Navegar al directorio frontend
cd cafe-system-frontend

# Instalar dependencias
npm install

# Iniciar en modo desarrollo
npm run dev

# Iniciar aplicación Electron (próximamente)
npm run electron-dev
```

## 🎯 Roadmap

- [x] Sistema de autenticación
- [x] Gestión de mesas
- [x] Sistema de órdenes
- [x] Panel de cocina
- [ ] Interfaz web
- [ ] Aplicación Electron
- [ ] Integración de pagos
- [ ] Modo offline
- [ ] Reportes y analytics

## 📚 Documentación

- **API**: Disponible en `/docs` o `/redoc` cuando el servidor está corriendo
- **Postman Collection**: Disponible en `/docs/postman`
- **Tests**: Ejecutar con `pytest tests/`

## 👥 Desarrollo

### Estructura de Carpetas

#### Backend
```
app/
├── auth/           # Autenticación
├── tables/         # Gestión de mesas
├── orders/         # Sistema de órdenes
├── kitchen/        # Panel de cocina
├── products/       # Gestión de productos
└── payments/       # Procesamiento de pagos
```

#### Frontend (En desarrollo)
```
src/
├── components/     # Componentes reutilizables
├── pages/         # Páginas principales
├── features/      # Módulos específicos
├── hooks/         # Custom hooks
├── stores/        # Estado global
├── api/           # Cliente API
└── types/         # Tipos TypeScript
```

## 📝 Licencia

[Tipo de licencia por definir]
