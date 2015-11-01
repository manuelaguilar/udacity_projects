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

movies = []

response["results"].append({"title":"Star Wars: Episode VII - The Force Awakens","release_date":"2015-12-18"})
response["results"].append({"title":"The Silence of the Lambs","release_date":"1991"})
response["results"].append({"title":"Shaun the Sheep","release_date":"2015"})

for movie_item in response["results"]:
  #small fix for titles with non-familiar unicode characters
  movie_name = urllib.quote(movie_item["title"].encode('utf8'))
  imdb_request = urllib.urlopen("http://www.omdbapi.com/?t="+movie_name+"&y="+str(dparser.parse(movie_item["release_date"]).year)+"&r=json")
  imdb_movie = imdb_request.read()
  imdb_movie_json = json.loads(imdb_movie)
  imdb_request.close()
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
  #print movie.title
  #print movie.trailer_youtube_url
  #print movie.poster_image_url
  #print movie_item
  movies.append(movie)

#movie = media.Movie("Toy Story",1993,"story_line here", "image_url_here","trailer_youtube_url_here")
#test = urllib.urlopen("http://www.omdbapi.com/?i=tt0067277&r=json")
#test = urllib.urlopen("http://www.omdbapi.com/?t=Batman v Superman: Dawn of Justice&r=json")

#info = test.read()
#info_formatted = json.loads(info)
#test.close()

#test2 = urllib.urlopen("http://api.traileraddict.com/?imdb=tt0067277")
#API v2 deprecated , use v3
#test2 = urllib.urlopen("http://gdata.youtube.com/feeds/api/videos/-/The-A-Team-trailer?max-results=1")
#print test2.read()
#test2.close()

#print info_formatted['Title']
#print info_formatted['Year']
#print info_formatted['Plot']
#print info_formatted['Poster']
#print info_formatted
#print movie.release_date

fresh_tomatoes.open_movies_page(movies)
