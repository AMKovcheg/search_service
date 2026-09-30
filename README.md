# search_service

Перед запуском необходимо создать вирутально окружение и установить все необходимые зависимости:
1. ```python3 -m venv venv```
2. ```source venv/bin/activate```
3. ```pip install -r requirements.txt```

Далее нужно запустить ElasticSearch:

```docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.1```


Теперь запуск самого сервиса и примеры работы:
1. ```uvicorn app.main:app --reload --host 0.0.0.0 --port 8000```
2. (все команды с curl нужно выполнять в отлельном терминале) ```curl -X POST "http://localhost:8000/import-csv?file_path=posts.csv"``` - импортируем posts.csv

Команда для поиска: ```curl -G "http://localhost:8000/api/v1/search" --data-urlencode "q=<текст поискового запроса>"```

Команда для удаления: ```curl -X DELETE "http://localhost:8000/api/v1/documents/<id удаляемого документа>```

Также можно выполнять эти search(GET) и delete с помощью Swagger UI на http://localhost:8000/docs#/