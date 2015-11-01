#!/usr/bin/python

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

import httplib2
import api_keys

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.

DEVELOPER_KEY = api_keys.YOUTUBE_API_KEY

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(options):
  #load working cacert.txt manually
  h = httplib2.Http()
  h = httplib2.Http(ca_certs='/Library/Python/2.7/site-packages/httplib2-0.9.2-py2.7.egg/httplib2/cacerts.txt')
  #override http parameter to load specific working cacert file
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=h, developerKey=DEVELOPER_KEY)
  #  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
  # Call the search.list method to retrieve results matching the specified
  # query term.
  search_response = youtube.search().list(
    q=options.q,
    part="id,snippet",order="relevance",type="video", #publishedAfter="2014-12-31T23:59:59Z",type="video",
    maxResults=options.max_results
  ).execute()

  videos = []
  channels = []
  playlists = []

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      findVideoResp = youtube.videos().list(part="statistics",id=search_result["id"]["videoId"]).execute()
      for foundVideo in findVideoResp.get("items",[]):
        videos.append("%s (%s) (%s)" % (search_result["snippet"]["title"],
                                 search_result["id"]["videoId"], 
				 foundVideo['statistics']['viewCount']))
    elif search_result["id"]["kind"] == "youtube#channel":
      channels.append("%s (%s)" % (search_result["snippet"]["title"],
                                   search_result["id"]["channelId"]))
    elif search_result["id"]["kind"] == "youtube#playlist":
      playlists.append("%s (%s)" % (search_result["snippet"]["title"],
                                    search_result["id"]["playlistId"]))

  print "Videos:\n", "\n".join(videos), "\n"
  print "Channels:\n", "\n".join(channels), "\n"
  print "Playlists:\n", "\n".join(playlists), "\n"


if __name__ == "__main__":
  print "Start."
  argparser.add_argument("--q", help="Search term", default="Google")
  argparser.add_argument("--max-results", help="Max results", default=25)
  args = argparser.parse_args()

  try:
    youtube_search(args)
  except HttpError, e:
    print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
