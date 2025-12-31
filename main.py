import poster_scraper as ps
from db_config import *

import mysql.connector
import streamlit as st
from PIL import Image
import random

def initialize_database():
    try:
        mydb = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            passwd=DB_PASS,
            port=DB_PORT,
            connection_timeout=5,
            database=DB_NAME
        )
    except Exception as e:
        st.error(f"MySQL connection error: {e}")
    else:
        return mydb

def sql_select_statement(mydb, query):
    try:
        my_cursor = mydb.cursor()
        my_cursor.execute(query)
        my_result = my_cursor.fetchall()
        return my_result
    except Exception as e:
        st.error(e)
        return []

def runtime_to_hour_minutes(runtime):
    runtime = int(runtime)
    hours = int(runtime // 60)
    minutes = int(runtime % 60)
    return f"{hours}h {minutes}m"

def show_movie_details(mydb, movie):
    st.subheader(movie[1])
    poster = ps.main(movie[1],movie[2].year)
    if poster:
        st.image(poster)
    st.write(f"Year: {movie[2].year}")
    if movie[3] >= 60:
        st.write(f"Runtime: {movie[3]} m\t({runtime_to_hour_minutes(movie[3])})")
    else:
        st.write(f"Runtime: {movie[3]} m")
    st.write(f"Rating: {movie[4]}")
    st.subheader("Watch on:")
    copies = sql_select_statement(mydb,f"SELECT DISTINCT F.Name FROM MediaCopy MC JOIN Format F ON F.FormatID = MC.FormatID JOIN MediaVideo MV ON MV.CopyID = MC.CopyID JOIN Video V ON V.VideoID = MV.VideoID WHERE V.Title = '{movie[1].replace("\'","\'\'")}'")
    for format in copies:
        st.image(Image.open(f"images/{format[0]}.png"),width=60)
    if st.button("Back to search"):
        st.session_state.selected_movie = None
        st.session_state.search_submitted = False
        st.rerun()

def main():
    # Connect to database
    mydb = initialize_database()

    db_size = int(sql_select_statement(mydb, "SELECT COUNT(*) FROM Video")[0][0])

    st.header("Caleb's Movies")

    # Initialize session state
    if "selected_movie" not in st.session_state:
        st.session_state.selected_movie = None
    if "recommended_movie" not in st.session_state:
        st.session_state.recommended_movie = None
    if "user_search" not in st.session_state:
        st.session_state.user_search = ""
    if "search_submitted" not in st.session_state:
        st.session_state.search_submitted = False
    if "show_all" not in st.session_state:
        st.session_state.show_all = False

    # If a movie is selected, show its detail page
    if st.session_state.selected_movie:
        show_movie_details(mydb, st.session_state.selected_movie)
        return

    def submit_search():
        st.session_state.search_submitted = True
        st.session_state.recommended_movie = None

    # Show all movies
    if st.button("Show all movies"):
        st.session_state.show_all = not st.session_state.show_all

    # User search input
    st.text_input(
        "Search collection",
        key="user_search",
        value=st.session_state.user_search,
        on_change=submit_search
    ).strip()

    if st.session_state.search_submitted and st.session_state.user_search:
        st.session_state.show_all = False
        results = sql_select_statement(mydb, f"SELECT * FROM video WHERE TITLE LIKE '%{st.session_state.user_search.replace("\'","\'\'")}%' ORDER BY TITLE ASC")
        if not results:
            st.write("No results found")
            st.subheader("Other movies")
            if st.session_state.recommended_movie is None:
                st.session_state.recommended_movie = sql_select_statement(mydb,f"SELECT * FROM video WHERE VideoID = {random.randint(0, db_size - 1)}")[0]
            rec_movie = st.session_state.recommended_movie
            # Button to select recommended movie
            button_key = f"rec_select_{rec_movie[0]}"
            if st.button(f"{rec_movie[1]} ({rec_movie[2].year})", key=button_key):
                st.session_state.selected_movie = rec_movie
                st.session_state.search_submitted = False
                st.rerun()
        else:
            for movie in results:
                # Button to select movie
                button_key = f"search_select_{movie[0]}"
                if st.button(f"{movie[1]} ({movie[2].year})", key=button_key):
                    st.session_state.selected_movie = movie
                    st.session_state.search_submitted = False
                    st.rerun()
    if st.session_state.show_all:
        results = sql_select_statement(mydb,f"SELECT * FROM video ORDER BY TITLE ASC")
        for movie in results:
            # Button to select movie
            button_key = f"all_select_{movie[0]}"
            if st.button(f"{movie[1]} ({movie[2].year})", key=button_key):
                st.session_state.selected_movie = movie
                st.session_state.search_submitted = False
                st.rerun()

if __name__ == "__main__":
    main()