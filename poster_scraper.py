from PyMovieDb import IMDB
import json

def retrieve_poster_by_id(imdb_id):
    try:
        imdb = IMDB()
        json_str = imdb.get_by_id(f"tt{imdb_id}")
        res = json.loads(json_str)
        return res["poster"]
    except Exception as e:
        return e

def main(imdb_id):
    retrieve_poster_by_id(imdb_id)

if __name__ == "__main__":
    main(imdb_id="")
