# Annia Apps - Suite de Aplicaciones para Química Computacional

Una suite de aplicaciones web modernas construidas con Angular 21 para análisis y cálculos en química computacional.

## 🚀 Características

### Easy Rate 2.0

Cálculo de constantes de velocidad con correcciones termodinámicas y de difusión basado en:

- Parseo de archivos Gaussian (.log, .txt, .out)
- Cálculo de entalpías y energías libres de Gibbs
- Aplicación de correcciones de tunelamiento (Wigner)
- Correcciones de difusión con parámetros de solvente
- Interfaz responsiva y amigable

## 📋 Requisitos Previos

- Node.js 18+
- npm 9+
- Angular CLI 21+

## 🔧 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/CesarGuzmanLopez/Apps-Annia.git

# Navegar a la carpeta del proyecto Angular
cd Apps-Annia/apps-annia

# Instalar dependencias
npm install
```

## 🏃 Ejecución

### Desarrollo

```bash
npm start
```

La aplicación estará disponible en `http://localhost:4200`

### Build para Producción

```bash
npm run build
```

Los archivos compilados estarán en `dist/apps-annia/`

## 📁 Estructura del Proyecto

```
apps-annia/
├── src/
│   ├── app/
│   │   ├── core/                          # Servicios centrales
│   │   ├── shared/                        # Componentes compartidos
│   │   ├── features/
│   │   │   ├── menu/                      # Componente de menú principal
│   │   │   └── easy-rate/                 # Aplicación Easy Rate
│   │   │       ├── models/                # Interfaces y tipos
│   │   │       ├── services/              # Servicios de cálculo
│   │   │       ├── easy-rate.component.ts
│   │   │       ├── easy-rate.component.html
│   │   │       └── easy-rate.component.scss
│   │   ├── app.ts                         # Componente raíz
│   │   ├── app.routes.ts                  # Configuración de rutas
│   │   └── app.scss
│   ├── main.ts
│   ├── styles.scss
│   └── index.html
├── angular.json
├── tsconfig.json
└── package.json
```

## 🎯 Uso de Easy Rate

1. **Abrir Easy Rate** desde el menú principal
2. **Cargar archivos Gaussian**:
   - React-1: Reactivo primario (requerido)
   - React-2: Reactivo secundario (opcional)
   - Transition state: Estado de transición (requerido)
   - Product-1: Producto primario (requerido)
   - Product-2: Producto secundario (opcional)

3. **Configurar parámetros**:
   - Temperatura en Kelvin (por defecto 298.15 K)
   - Degeneracidad de la ruta de reacción
   - Activar tunelamiento (Wigner)
   - Configurar difusión (opcional)

4. **Ejecutar cálculo**: Click en "Data ok, Run"

## 📊 Modelos Soportados

Los archivos Gaussian deben contener:

- Energía electrónica (SCF Done)
- Energía de punto cero (Zero-point correction)
- Energía libre de Gibbs térmica
- Frecuencias vibracionales (para estados de transición)

## ⚙️ Servicios Principales

### `EasyRateCalculatorService`

Realiza los cálculos termodinámicos:

- Cálculo de constantes de velocidad (TST)
- Aplicación de correcciones de tunelamiento
- Correcciones de difusión
- Formateo de resultados

### `EstructuraService`

Gestiona la lectura de archivos Gaussian:

- Parseo de datos de archivos
- Validación de estructuras
- Extracción de propiedades termodinámicas

## 🎨 Diseño

- **Tema**: Clearlooks (ttkthemes)
- **Colores principales**:
  - Azul: #3498db
  - Verde: #27ae60
  - Rojo: #e74c3c
  - Púrpura: #667eea / #764ba2

## 🔐 Licencia

MIT

## 👨‍💻 Autor

Cesar Gerardo Guzman Lopez

## 📞 Soporte

Para reportar problemas o sugerencias, abra un issue en el repositorio.

---

**Nota**: Esta es la versión web Angular de Easy Rate 2.0. Para la versión de escritorio con Tkinter, consulte la carpeta `/Easy-rate` en el repositorio raíz.
