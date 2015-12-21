#!/usr/bin/python


#APIS
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

import httplib2
import tmdbsimple as tmdb

import api_keys

#PROJECT
import media
import urllib
import json
import webbrowser
import fresh_tomatoes
import dateutil.parser as dparser

DEVELOPER_KEY = api_keys.YOUTUBE_API_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

tmdb.API_KEY=api_keys.TMDB_API_KEY


top20 = tmdb.Movies()
response = top20.popular(page="1")

def add_movie(title, year):
  response["results"].append({"title":title,"release_date":year})

movies = []

add_movie("Star Wars The Force Awakens","2015")
add_movie("The Silence of the Lambs","1991")
add_movie("Shaun the Sheep", "2015")
add_movie("The English Patient", "1996")

for movie_item in response["results"]:
  #small fix for titles with non-familiar unicode characters
  movie_name = urllib.quote(movie_item["title"].encode('utf8'))
  imdb_request = urllib.urlopen("http://www.omdbapi.com/?t="+movie_name+"&y="+str(dparser.parse(movie_item["release_date"]).year)+"&r=json")
  imdb_movie = imdb_request.read()
  imdb_movie_json = json.loads(imdb_movie)
  imdb_request.close()
  #print imdb_movie_json
  #get youtube trailer url
  h = httplib2.Http()
  h = httplib2.Http(ca_certs='/Library/Python/2.7/site-packages/httplib2-0.9.2-py2.7.egg/httplib2/cacerts.txt')
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=h, developerKey=DEVELOPER_KEY)
  print "Youtube search for : " + movie_item["title"]+" trailer"
  search_response = youtube.search().list(
    q=movie_item["title"]+" trailer", maxResults=1,
    part="id,snippet",order="relevance",type="video", #publishedAfter="2014-12-31T23:59:59Z",type="video",
  ).execute()

  movie = media.Movie(movie_item["title"],imdb_movie_json["Year"],imdb_movie_json["Plot"],imdb_movie_json["Poster"],None)
  for search_result in search_response.get("items", []):
    movie.trailer_youtube_url = "https://www.youtube.com/watch?v=" + search_result["id"]["videoId"]
  movies.append(movie)



fresh_tomatoes.open_movies_page(movies)
