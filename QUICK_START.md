# ⚡ QUICK START - Comienza en 5 minutos

## 1️⃣ Clonar o descargar

```bash
git clone https://github.com/TU_USUARIO/airflow-cloud.git
cd airflow-cloud
```

## 2️⃣ Setup local (opcional)

```bash
# Instalar dependencias
pip install -r requirements.txt

# Levantar con Docker Compose
docker-compose up -d

# Esperar 30 segundos...

# Acceder a Airflow
# URL: http://localhost:8080
# Usuario: airflow
# Contraseña: airflow
```

## 3️⃣ Deploy a la nube

### Railway (Más fácil)
```bash
railway login
railway init
railway add --postgres
railway add --redis
railway up
```

### Heroku
```bash
heroku create tu-app-name
heroku addons:create heroku-postgresql
heroku addons:create heroku-redis
git push heroku main
```

## ✅ Verificar que funciona

```bash
# Ver DAGs
python -m py_compile dags/dag_principal.py

# Ver logs
docker-compose logs -f airflow-scheduler

# Test imports
python -c "from dags.dag_principal import dag; print('✅ DAG OK')"
```

## 📊 Tu primer DAG

En Airflow UI:
1. Busca: `airflow_pipeline_diario`
2. Click en el DAG
3. Botón "Trigger DAG"
4. Espera a que termine
5. ¡Listo! 🎉

## 🛑 Parar servicios

```bash
docker-compose down
```

## 📝 Próximos pasos

- Edita `dags/dag_principal.py` para tu lógica
- Crea nuevos DAGs en `dags/`
- Agrega tareas en `dags/etls/` y `dags/pipelines/`
- Push a GitHub → GitHub Actions valida automáticamente
- Tu plataforma cloud auto-deploya

## 🆘 Problemas?

```bash
# Ver logs del scheduler
docker-compose logs airflow-scheduler

# Ver logs del webserver
docker-compose logs airflow-webserver

# Reiniciar
docker-compose restart
```

---

**¡Ya estás listo!** Completa los pasos y tendrás Airflow corriendo. 🚀
