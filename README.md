# Async_API_sprint_4
Yandex practicum


## Установка 
Клонируем репозиторий на локальную машину:

```$ git clone https://github.com/Rusich90/Async_API_sprint_4.git```

В корневую директорию проекта нужно перенести папку с вольюмом постгреса из спринта №2 и названием "postgresql"

В корневую директорию проекта нужно перенести папку с вольюмом ElasticSearch из спринта №3 и названием "elastic" (можно
пустой - главное чтобы индекс соответствовал описанию)

Индексы эластика должны соответствовать следующим:

 ```
curl -XPUT http://127.0.0.1:9200/genres -H 'Content-Type: application/json' -d'
{
  "settings": {
    "refresh_interval": "1s",
    "analysis": {
      "filter": {
        "english_stop": {
          "type":       "stop",
          "stopwords":  "_english_"
        },
        "english_stemmer": {
          "type": "stemmer",
          "language": "english"
        },
        "english_possessive_stemmer": {
          "type": "stemmer",
          "language": "possessive_english"
        },
        "russian_stop": {
          "type":       "stop",
          "stopwords":  "_russian_"
        },
        "russian_stemmer": {
          "type": "stemmer",
          "language": "russian"
        }
      },
      "analyzer": {
        "ru_en": {
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "english_stop",
            "english_stemmer",
            "english_possessive_stemmer",
            "russian_stop",
            "russian_stemmer"
          ]
        }
      }
    }
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "id": {
        "type": "keyword"
      },
      "name": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "description": {
        "type": "text",
        "analyzer": "ru_en"
      }
    }
  }
}'


curl -XPUT http://127.0.0.1:9200/persons -H 'Content-Type: application/json' -d'
{
  "settings": {
    "refresh_interval": "1s",
    "analysis": {
      "filter": {
        "english_stop": {
          "type":       "stop",
          "stopwords":  "_english_"
        },
        "english_stemmer": {
          "type": "stemmer",
          "language": "english"
        },
        "english_possessive_stemmer": {
          "type": "stemmer",
          "language": "possessive_english"
        },
        "russian_stop": {
          "type":       "stop",
          "stopwords":  "_russian_"
        },
        "russian_stemmer": {
          "type": "stemmer",
          "language": "russian"
        }
      },
      "analyzer": {
        "ru_en": {
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "english_stop",
            "english_stemmer",
            "english_possessive_stemmer",
            "russian_stop",
            "russian_stemmer"
          ]
        }
      }
    }
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "id": {
        "type": "keyword"
      },
      "name": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "birth_date": {
        "type": "date"
      }
    }
  }
}'


curl -XPUT http://127.0.0.1:9200/movies -H 'Content-Type: application/json' -d'
{
  "settings": {
    "refresh_interval": "1s",
    "analysis": {
      "filter": {
        "english_stop": {
          "type":       "stop",
          "stopwords":  "_english_"
        },
        "english_stemmer": {
          "type": "stemmer",
          "language": "english"
        },
        "english_possessive_stemmer": {
          "type": "stemmer",
          "language": "possessive_english"
        },
        "russian_stop": {
          "type":       "stop",
          "stopwords":  "_russian_"
        },
        "russian_stemmer": {
          "type": "stemmer",
          "language": "russian"
        }
      },
      "analyzer": {
        "ru_en": {
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "english_stop",
            "english_stemmer",
            "english_possessive_stemmer",
            "russian_stop",
            "russian_stemmer"
          ]
        }
      }
    }
  },
  "mappings": {
    "dynamic": "strict",
    "properties": {
      "id": {
        "type": "keyword"
      },
      "imdb_rating": {
        "type": "float"
      },
      "type": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "analyzer": "ru_en",
        "fields": {
          "raw": {
            "type":  "keyword"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "genres_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "directors_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "actors_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "writers_names": {
        "type": "text",
        "analyzer": "ru_en"
      },
      "actors": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      },
      "directors": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      },
      "writers": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      },
      "genres": {
        "type": "nested",
        "dynamic": "strict",
        "properties": {
          "id": {
            "type": "keyword"
          },
          "name": {
            "type": "text",
            "analyzer": "ru_en"
          }
        }
      }
    }
  }
}'
  ```

 
Создаём файл .env (присутствует пример) в директории "postgres_to_es" с секретными данными для доступа к Postgres:
 
 ```
    DSN__DBNAME=movies_database  # имя базы данных
    DSN__USER=<your_login> # логин для подключения к базе данных (установите свой)
    DSN__PASSWORD=<your_password> # пароль для подключения к БД (установите свой)
    DSN__HOST=db # название сервиса (контейнера)
    DSN__PORT=5432 # порт для подключения к БД
 
  ```

Создаём файл .env (присутствует пример) в директории "src/core" с данными хостов redis и es:
 
 ```
    ELASTIC_HOST=es # название сервиса (контейнера) elasticsearch
    REDIS_HOST=redis # название сервиса (контейнера) redis
    EXPIRE_TIME=300 # время кеширования в редисе в секундах
 
  ```
 
Запускаем сборку докера:
 
 ```$ docker-compose up```
 
Вы прекрасны! (но это не точно) =)

Желательно дождаться когда ЭТЛ процесс перегонит все данные из постгреса

Доступ к документации http:/localhost/api/openapi/


Тесты запускать из директории src/tests/functional:

 ```$ docker-compose up```


При получении списка за пагинацию отвечает параметр pagination (реализован метод бесконечной прокрутки), после первого запроса списка нужно каждый запрос добавлять параметр pagination (он обновлеятся каждый раз)
