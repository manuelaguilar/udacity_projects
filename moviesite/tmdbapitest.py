#!/usr/bin/python

import tmdbsimple as tmdb
import api_keys 

tmdb.API_KEY=api_keys.TMBD_API_KEY

top20 = tmdb.Movies()
response = top20.top_rated(page="1")

for movie in response["results"]:
  print movie["title"]

#print response
