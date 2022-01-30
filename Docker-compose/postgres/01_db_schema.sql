create schema content;
create table if not exists content.film_work(
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    certificate TEXT,
    file_path TEXT,
    rating FLOAT,
    type TEXT not null,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);
create table if not exists content.genre(
    id uuid PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);
create table if not exists content.genre_film_work(
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    genre_id uuid NOT NULL,
    created_at timestamp with time zone
);
create table if not exists content.person(
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    birth_date date,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);
create table if not exists content.person_film_work(
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role text NOT NULL,
    created_at timestamp with time zone
);
create unique index film_work_genre_idx ON content.genre_film_work(film_work_id, genre_id);
create unique index film_work_person_role_idx ON content.person_film_work(film_work_id, person_id, role);