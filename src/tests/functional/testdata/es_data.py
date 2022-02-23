import json

genres = [
       {"id": "120a21cf-9097-479e-904a-13dd7198c1dd", "name": "Adventure", "description": None},
       {"id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", "name": "Action", "description": None},
       {"id": "6c162475-c7ed-4461-9184-001ef3d9f26e", "name": "Sci-Fi", "description": None},
       {"id": "b92ef010-5e4c-4fd0-99d6-41b6456272cd", "name": "Fantasy", "description": None},
]

persons = [
       {"id": "354d7532-386f-48d1-83ab-42c0ff5f146b", "name": "Dan Connors", "birth_date": None},
       {"id": "49fe7794-de90-4274-9a50-2be80ca04330", "name": "Clint Bajakian", "birth_date": None},
       {"id": "509c1168-0ced-4704-a3b9-f17b9dc37667", "name": "Lindsay Duncan", "birth_date": None},
       {"id": "5b4bf1bc-3397-4e83-9b17-8b10c6544ed1", "name": "Reshan Fernando", "birth_date": None},
       {"id": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a", "name": "George Lucas", "birth_date": None},
       {"id": "b505845f-d7bc-4271-a59d-5dc16a641cac", "name": "Jon Burton", "birth_date": None},
       {"id": "d115d4c3-daf9-45ba-8034-1eb07b3be2f3", "name": "Rachid Oumakhlouf", "birth_date": None},
       {"id": "e424a80e-4cf6-4ada-8409-f82056a54564", "name": "Nils Bento-Connault", "birth_date": None},

]

movies = [
    {"id": "d755d600-296a-4c91-98b9-17107a5e63f5",
     "imdb_rating": 8.7,
     "type": "movie",
     "title": "A Gold Star Kid",
     "description": "9 years old Matt is finding a 20 euro bill on the pavement. Matt is seeing a soldier in the restaurant which reminds his late father who was a soldier, and he changes his mind to pay it ...",
     "genres_names": ["Fantasy", "Adventure"],
     "directors_names": ["Reshan Fernando"],
     "actors_names": ["Rachid Oumakhlouf", "Nils Bento-Connault"],
     "writers_names": ["Reshan Fernando"],
     "actors": [{"id": "d115d4c3-daf9-45ba-8034-1eb07b3be2f3", "name": "Rachid Oumakhlouf"},
                {"id": "e424a80e-4cf6-4ada-8409-f82056a54564", "name": "Nils Bento-Connault"}],
     "directors": [{"id": "8d026eb1-aaab-4b1f-b9f9-cd64bb6d46fc", "name": "Reshan Fernando"}],
     "writers": [{"id": "8d026eb1-aaab-4b1f-b9f9-cd64bb6d46fc", "name": "Reshan Fernando"}],
     "genres": [{"id": "120a21cf-9097-479e-904a-13dd7198c1dd", "name": "Adventure"},
                {"id": "b92ef010-5e4c-4fd0-99d6-41b6456272cd", "name": "Fantasy"}]},
    {"id": "daae47e4-cbd0-4ffd-a150-55201b357d5b",
     "imdb_rating": 8.2,
     "type": "movie",
     "title": "Lego Star Wars: The Video Game",
     "description": "Play through the star wars prequel trilogy in episodes 1,2,and 3, in lego.",
     "genres_names": ["Adventure", "Action"],
     "directors_names": ["Jon Burton"],
     "actors_names": ["Lindsay Duncan"],
     "writers_names": ["George Lucas"],
     "actors": [{"id": "509c1168-0ced-4704-a3b9-f17b9dc37667", "name": "Lindsay Duncan"}],
     "directors": [{"id": "b505845f-d7bc-4271-a59d-5dc16a641cac", "name": "Jon Burton"}],
     "writers": [{"id": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a", "name": "George Lucas"}],
     "genres": [{"id": "120a21cf-9097-479e-904a-13dd7198c1dd", "name": "Adventure"},
                {"id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", "name": "Action"}]},
    {"id": "d6a7409f-87cd-49d7-8803-951a7352c2ce",
     "imdb_rating": 6.2,
     "type": "movie",
     "title": "Star Wars: Obi-Wan",
     "description": "This videogame is focused on Obi Wan Kenobi, it tells you the story beneath Chapter One: The Ghost Meneace and how it started and all Obi Wan passed trough in this chapter by playing with him. This videogame is only for Xbox",
     "genres_names": ["Action", "Sci-Fi"],
     "directors_names": ["Dan Connors"],
     "actors_names": ["Clint Bajakian"],
     "writers_names": ["George Lucas"],
     "actors": [{"id": "49fe7794-de90-4274-9a50-2be80ca04330", "name": "Clint Bajakian"}],
     "directors": [{"id": "354d7532-386f-48d1-83ab-42c0ff5f146b", "name": "Dan Connors"}],
     "writers": [{"id": "a5a8f573-3cee-4ccc-8a2b-91cb9f55250a", "name": "George Lucas"}],
     "genres": [{"id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff", "name": "Action"},
                {"id": "6c162475-c7ed-4461-9184-001ef3d9f26e", "name": "Sci-Fi"}]},
]


def data_for_elastic():
    json_list = []
    for record in persons:
        index_info = {'index': {'_index': 'persons', '_id': record['id']}}
        json_list.append(index_info)
        json_list.append(record)
    for record in movies:
        index_info = {'index': {'_index': 'movies', '_id': record['id']}}
        json_list.append(index_info)
        json_list.append(record)
    for record in genres:
        index_info = {'index': {'_index': 'genres', '_id': record['id']}}
        json_list.append(index_info)
        json_list.append(record)

    json_list = '\n'.join(json.dumps(j) for j in json_list)
    json_list += '\n'
    return json_list
