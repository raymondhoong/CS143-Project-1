\COPY project1.artist(artist_id, artist_name) FROM '/home/cs143/data/artist.csv' DELIMITER ',' QUOTE '"' CSV;
\COPY project1.song(song_id, artist_id, song_name, page_link) FROM '/home/cs143/data/song.csv' DELIMITER ',' QUOTE '"'  CSV;
\COPY project1.token(song_id, token, count) FROM '/home/cs143/data/token.csv' DELIMITER ',' QUOTE '"' CSV;
