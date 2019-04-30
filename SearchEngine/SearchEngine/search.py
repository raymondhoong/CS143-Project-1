#!/usr/bin/python3

import psycopg2
import re
import string
import sys

_PUNCTUATION = frozenset(string.punctuation)

def _remove_punc(token):
    """Removes punctuation from start/end of token."""
    i = 0
    j = len(token) - 1
    idone = False
    jdone = False
    while i <= j and not (idone and jdone):
        if token[i] in _PUNCTUATION and not idone:
            i += 1
        else:
            idone = True
        if token[j] in _PUNCTUATION and not jdone:
            j -= 1
        else:
            jdone = True
    return "" if i > j else token[i:(j+1)]

def _get_tokens(query):
    rewritten_query = []
    tokens = re.split('[ \n\r]+', query)
    for token in tokens:
        cleaned_token = _remove_punc(token)
        if cleaned_token:
            if "'" in cleaned_token:
                cleaned_token = cleaned_token.replace("'", "''")
            rewritten_query.append(cleaned_token)
    return rewritten_query



def search(query, query_type):
    
    tokens = _get_tokens(query)
    
    num_tokens = len(tokens)
    
    if num_tokens == 0:
        raise ValueError("No results! Must enter a query!")
    
    col = "song_name, artist_name, Y.page_link"
    
    table = """SELECT L.song_id, SUM(R.score) as score
        FROM project1.token L
        JOIN project1.tfidf R
        ON L.song_id = R.song_id AND L.token = R.token
        WHERE L.token = '{first}'""".format(first = tokens[0])

    for x in range(1, num_tokens):
        table = table + " OR L.token = '{cur_token}'".format(cur_token = tokens[x])

    table = table + " GROUP BY L.song_id"

    if query_type == "AND":
        table + " HAVING COUNT(song_id) = {count}".format(count = num_tokens)
    
    end_clause = """JOIN project1.song Y ON X.song_id = Y.song_id
        JOIN project1.artist Z ON Y.artist_id = Z.artist_id
        ORDER BY score DESC"""
    
    sql_query = "SELECT {c} FROM ({r}) X {end};".format(c = col, r = table, end = end_clause)

    """TODO
    Your code will go here. Refer to the specification for projects 1A and 1B.
    But your code should do the following:
    1. Connect to the Postgres database.
    2. Graciously handle any errors that may occur (look into try/except/finally).
    3. Close any database connections when you're done.
    4. Write queries so that they are not vulnerable to SQL injections.
    5. The parameters passed to the search function may need to be changed for 1B. 
    """

    try:
        connection = psycopg2.connect(user="cs143",
                                  password="cs143",
                                  host="localhost",
                                  database="searchengine")
    except psycopg2.Error as e:
        print(e.pgerror)

    try:
        cursor = connection.cursor()
    except psycopg2.Error as e:
        print(e.pgerror)

    try:
        cursor.execute(sql_query)
    except psycopg2.Error as e:
        print(e.pgerror)

    rows = []
    row = cursor.fetchall()
    for result in row:
        rows.append(result)

    connection.close()
    
    return rows

if __name__ == "__main__":
    if len(sys.argv) > 2:
        result = search(' '.join(sys.argv[2:]), sys.argv[1].lower())
        print(result)
    else:
        print("USAGE: python3 search.py [or|and] term1 term2 ...")

