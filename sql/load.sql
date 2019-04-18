\COPY project1.artist(artist_id, artist_name) FROM '/home/cs143/data/artist.csv' WITH CSV;
\COPY project1.song(song_id, artist_id, song_name, url_suffix) FROM '/home/cs143/data/song.csv' WITH CSV;
\COPY project1.token(song_id, word, word_freq) FROM '/home/cs143/data/token.csv' WITH CSV;