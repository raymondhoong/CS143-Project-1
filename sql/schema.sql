DROP SCHEMA IF EXISTS project1 CASCADE;
CREATE SCHEMA IF NOT EXISTS project1;

CREATE TABLE IF NOT EXISTS project1.artist (
        artist_id                       smallint,
        artist_name                     varchar(45) NOT NULL,
        PRIMARY KEY (artist_id)
);

CREATE TABLE IF NOT EXISTS project1.song (
        song_id                         integer,
        artist_id                       smallint NOT NULL,
        song_name                       varchar(80) NOT NULL,
        url_suffix                      varchar(110) NOT NULL,
        PRIMARY KEY (song_id),
        FOREIGN KEY (artist_id) REFERENCES project1.artist(artist_id)
);

CREATE TABLE IF NOT EXISTS project1.token (
        song_id                         integer,
        word                            varchar(110),
        word_freq                       smallint NOT NULL,
        PRIMARY KEY (song_id, word),
        FOREIGN KEY (song_id) REFERENCES project1.song(song_id)
);

CREATE TABLE IF NOT EXISTS project1.tfidf (
        song_id                         integer,
        word                            varchar(110),
        word_tfidf                      double precision NOT NULL,
        PRIMARY KEY (song_id, word),
        FOREIGN KEY (song_id, word) REFERENCES project1.token(song_id, word),
        FOREIGN KEY (song_id) REFERENCES project1.song(song_id)
);