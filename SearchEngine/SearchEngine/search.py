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



def search(query_type, offset, query):
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

        
    tokens = _get_tokens(query)
    
    qtype = query_type.upper()
    print(qtype)
    num_tokens = len(tokens)
    
    if num_tokens == 0:
        raise ValueError("No results! Must enter a query!")
    
    col = "song_name, artist_name, Y.page_link"
    
    table = """SELECT L.song_id, SUM(R.score) as score
        FROM project1.token L
        JOIN project1.tfidf R
        ON L.song_id = R.song_id AND L.token = R.token
        WHERE L.token = LOWER('{first}')""".format(first = tokens[0])

    for x in range(1, num_tokens):
        table = table + " OR L.token = LOWER('{cur_token}')".format(cur_token = tokens[x])

    table = table + " GROUP BY L.song_id"

    if qtype == "AND":
        table = table + " HAVING COUNT(L.song_id) = {count}".format(count = num_tokens)
    
    end_clause = """JOIN project1.song Y ON X.song_id = Y.song_id
        JOIN project1.artist Z ON Y.artist_id = Z.artist_id
        ORDER BY score DESC"""

    sql_query = "SELECT {c} FROM ({r}) X {end};".format(c = col, r = table, end = end_clause)

    print(sql_query)

    """START RAYMOND LIN
    Make a unique materialized view name"""
    view_name = query_type
    i = 0
    while i != len(query):
        if query[i] == ' ':
            view_name += "_"
        else:
            view_name += query[i]
        i += 1

    view_name += "_query"

    """Delete existing views that aren't equal to current view"""
    view_lookup_query = "SELECT relname FROM pg_class WHERE relname NOT LIKE 'tfidf' AND relname NOT LIKE '{var}' AND relkind LIKE 'm';".format(var = view_name)
    print(view_lookup_query)
    try:
        cursor.execute(view_lookup_query)
    except psycopg2.Error as e:
        print(e.pgerror)

    views = cursor.fetchall()
    for name in views:
        print(name[0])
        if name[0].strip('\)\(') != view_name:
            delete_query = "DROP MATERIALIZED VIEW IF EXISTS project1.{var};".format(var = name[0].strip('\)\('))
            print(delete_query)
            try:
                cursor.execute(delete_query)
            except psycopg2.Error as e:
                print(e.pgerror)
            
    """Check if materialized view already exists"""
    check_query = "SELECT 1 FROM pg_class WHERE relname LIKE '{var}';".format(var = view_name) 

    try:
        print(check_query)
        cursor.execute(check_query)
    except psycopg2.Error as e:
        print(e.pgerror)

    value = cursor.fetchone()
    connection.commit()
    connection.close()
    if value is not None and value[0] == 1:
        print("view was found!")
    else:
        print("view not found - creating one now")
        materialized_query = "CREATE MATERIALIZED VIEW IF NOT EXISTS project1.{name} AS {query};".format(name = view_name, query = sql_query)    
        print(materialized_query)
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
            cursor.execute(materialized_query)
        except psycopg2.Error as e:
            print(e.pgerror)

        connection.commit()
        connection.close()
        
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

    short_query = "SELECT * FROM project1.{name} LIMIT 20 OFFSET {amount};".format(name = view_name, amount = offset)
    
    try:
        cursor.execute(short_query)
    except psycopg2.Error as e:
        print(e.pgerror)

    rows = []
    row = cursor.fetchall()
    for result in row:
        rows.append(result)

    length_query = "SELECT COUNT(*) FROM project1.{name};".format(name = view_name)
    try:
        cursor.execute(length_query)
    except psycopg2.Error as e:
        print(e.pgerror)

    length = cursor.fetchone()
    rows.append(length)
        
    connection.close()
    
    return rows

if __name__ == "__main__":
    if len(sys.argv) > 2:
        result = search(sys.argv[1].lower(), sys.argv[2], ' '.join(sys.argv[3:]))
        print(result)
    else:
        print("USAGE: python3 search.py [or|and] term1 term2 ...")

