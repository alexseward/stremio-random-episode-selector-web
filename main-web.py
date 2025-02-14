import requests
import random
import webbrowser
import imdb
import yaml

globalLink = ''

ia = imdb.Cinemagoer()

# Uses IMDb API to find the IMDb ID of the series
def findIMDBid(name):
    movie = ia.search_movie(name)[0]
    return f'tt{movie.movieID}'

# Takes season:episode and splits into [season, episode]
def processEpisodeCode(code):
    splitCode = code.split(':')
    return splitCode

# Reads list, returns list with [showname, episodecode, episodelink, episodename, season#, episode#]
def readListandChooseRandom():
    with open("list.yaml") as seriesListFile:
        seriesList = yaml.safe_load(seriesListFile)['series']

    # Choose random show from list first    
    showEntry = random.choice(seriesList)

    seasons = None
    extras = None

    # Process the data (seasons, extras) or define name
    if isinstance(showEntry, dict):
        nameOfShow = list(showEntry.keys())[0]
        if 'seasons' in showEntry[nameOfShow]:
            seasons = showEntry[nameOfShow]['seasons']
        if 'extra' in showEntry[nameOfShow]:
            extras = showEntry[nameOfShow]['extra']
    else:
        nameOfShow = showEntry

    id = findIMDBid(nameOfShow)
    episodeList = []

    # Use Cinemeta addon API to get metadata from the IMDb ID of the show
    r = requests.get(f"https://v3-cinemeta.strem.io/meta/series/{id}.json")
    showMetadata = r.json()

    # Adds episodes to random pool; only include seasons greater than 0
    for episode in showMetadata['meta']['videos']:
        # Ensure 'season' exists and is greater than 0
        if 'season' in episode and episode['season'] > 0:  
            if seasons is None or (episode['season'] in range(seasons[0], seasons[1] + 1)):
                episodeList.append(f"{episode['season']}:{episode['number']}")

    # Adds extras if there are any to random episode pool, ensuring they aren't Season 0
    if extras is not None:
        for episode in extras:
            if 'season' in episode and episode['season'] > 0:  # Ensure 'season' exists and is greater than 0
                episodeList.append(f"{episode['season']}:{episode['number']}")

    if not episodeList:  # Check if episodeList is empty
        return [nameOfShow, None, None, None, None, None]  # Handle the case where no valid episodes exist

    finalEpisode = random.choice(episodeList)
    seasonAndEpisodeNumber = processEpisodeCode(finalEpisode)
    finalEpisodeName = "Something went wrong"

    # Find the name of the episode
    for episode in showMetadata['meta']['videos']:
        if (episode['season'] == int(seasonAndEpisodeNumber[0])) and (episode['number'] == int(seasonAndEpisodeNumber[1])):
            finalEpisodeName = episode.get('title') or episode.get('name', "Something went wrong")

    finalLink = f"https://web.stremio.com/#/detail/series/{id}/{id}%3A{seasonAndEpisodeNumber[0]}%3A{seasonAndEpisodeNumber[1]}"

    return [nameOfShow, finalEpisode, finalLink, finalEpisodeName, seasonAndEpisodeNumber[0], seasonAndEpisodeNumber[1]]

def roll():
    finalSelection = readListandChooseRandom()

    print(f"Show selected: {finalSelection[0]}")
    print(f"Season: {finalSelection[4]}")
    print(f"Episode: {finalSelection[5]}")
    print(f"Name: {finalSelection[3]} \n")

    global globalLink
    globalLink = finalSelection[2]

print("Stremio Random Episode Chooser\n")
roll()

while True: 
    query = input('Would you like to reroll? (y/n) ') 
    Fl = query[0].lower() 
    if query == '' or Fl not in ['y', 'n']: 
        print('Please answer with yes or no!') 
    else: 
        if Fl == 'y': 
            print()
            roll()
        elif Fl == 'n': 
            webbrowser.open(globalLink)
            break
