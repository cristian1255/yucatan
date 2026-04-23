# Airflow Cloud - Pipeline Automatizado

Pipeline ETL completo con Apache Airflow para procesamiento de datos viales.

## 🚀 Features

✅ Airflow 2.9.1 con CeleryExecutor  
✅ PostgreSQL + Redis  
✅ Docker optimizado  
✅ GitHub Actions CI/CD  
✅ Listo para Railway, Heroku, Render  
✅ Scraper de datos viales  
✅ Pipeline ETL completo  

## 📋 Requisitos

- Python 3.12+
- Docker (opcional)
- Git
- Cuenta en plataforma cloud (Railway, Heroku, Render)

## 🔧 Setup Local (Opcional)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Inicializar Airflow
export AIRFLOW_HOME=./airflow
airflow db init

# Crear usuario
airflow users create \
  --username admin \
  --password admin \
  --firstname Admin \
  --lastname User \
  --role Admin

# Levantar con Docker Compose
docker-compose up -d
```

Acceder a: `http://localhost:8080`

## ☁️ Deploy en la Nube

### Railway (Recomendado)

```bash
# Login
railway login

# Crear proyecto
railway init

# Agregar servicios
railway add --postgres
railway add --redis

# Deploy
railway up
```

### Heroku

```bash
heroku create tu-app-name
heroku addons:create heroku-postgresql
heroku addons:create heroku-redis

git push heroku main
```

### Render

1. Conectar GitHub a Render
2. Deploy automático desde el repo

## 📁 Estructura

```
.
├── dags/                    # DAGs de Airflow
│   ├── dag_principal.py
│   ├── etls/
│   │   └── etl_viales.py
│   └── pipelines/
│       └── scraper_viales.py
├── Dockerfile              # Imagen Docker
├── requirements.txt        # Dependencias
├── docker-compose.yml      # Desarrollo local
├── .github/workflows/      # CI/CD
├── .devcontainer/          # VSCode Remote
└── Procfile               # Para Heroku/Railway
```

## 🔄 Pipeline

1. **DAG Principal**: `dag_principal.py` - Ejecuta diariamente a las 00:00
2. **ETL Viales**: `etl_viales.py` - Procesa datos viales
3. **Scraper**: `scraper_viales.py` - Obtiene URLs de la SCT

## 🔐 Variables de Entorno

Copia `.env.example` a `.env`:

```bash
cp .env.example .env
```

Edita con tus valores:
- `DATABASE_URL` - PostgreSQL
- `REDIS_URL` - Redis
- `_AIRFLOW_WWW_USER_PASSWORD` - Contraseña Airflow

## ✅ CI/CD Automático

GitHub Actions valida automáticamente en cada push:
- Validación de sintaxis Python
- Linting
- Test de imports
- Build de Docker image

## 📊 Monitoreo

Accede a Airflow UI en:
- Local: `http://localhost:8080`
- Cloud: `https://tu-app.railway.app` (o tu plataforma)

Usuario: `airflow`  
Contraseña: (la que configuraste)

## 🛠️ Troubleshooting

### "DAG not appearing"
```bash
python dags/dag_principal.py
```

### "Database connection failed"
Verifica DATABASE_URL está configurada correctamente

### "Docker build failed"
```bash
docker build --no-cache -t airflow-cloud .
```

## 📝 Logs

```bash
# Local
docker-compose logs -f airflow-scheduler

# Railway
railway logs -s scheduler

# Heroku
heroku logs --tail
```

## 🤝 Contribution

1. Fork el repo
2. Create tu rama: `git checkout -b feature/mi-feature`
3. Commit cambios: `git commit -m "feat: descripción"`
4. Push: `git push origin feature/mi-feature`
5. Pull Request

## 📄 Licencia

MIT

## 📞 Soporte

- Revisa logs en tu plataforma cloud
- Verifica variables de entorno
- Valida DAGs localmente

---

**Hecho con ❤️ para SCT Viales + Yucatán**
