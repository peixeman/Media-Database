import wikipedia

def remove_supplemental_title_info(movie_title):
    if "(" in movie_title:
        movie_title = movie_title[:movie_title.find("(") - 1]
    return movie_title

def find_movie_match(articles, title, year):
    for article in articles:
        if f"{title.lower()} ({str(year)} film)" in article.lower():
            return article
    for article in articles:
        if f"{title.lower()} (film)" == article.lower():
            return article
    for article in articles:
        if title.lower() in article.lower() or "film" in article.lower() or str(year) in article.lower():
            return article
    return articles[0]

def check_percentage_of_word_matches(img_url, movie_title):
    match_counter = 0
    title_words = movie_title.lower().split()
    for word in title_words:
        if word in img_url.lower():
            match_counter += 1
    return match_counter / len(title_words)

def main(title, year):
    title = remove_supplemental_title_info(title)
    try:
        articles = wikipedia.search(title, results=20)
    except Exception as e:
        return e
    else:
        movie_wiki = wikipedia.page(find_movie_match(articles,title,year),auto_suggest=False)

        for image in movie_wiki.images:
            if "poster" in image.lower():
                return image
        for image in movie_wiki.images:
            if title.lower() in image.lower():
                return image
        matches = []
        for image in movie_wiki.images:
            match_percentage = check_percentage_of_word_matches(image, title)
            matches.append([match_percentage, image])
        if max(matches, key=lambda x: x[0])[0] <= 0.5:
            return None
        return max(matches, key=lambda x: x[0])[1]

if __name__ == "__main__":
    main(title="",year="")
