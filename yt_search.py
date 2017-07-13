#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para buscar vídeos en youtube.
Usa una autenticación diferente al módulo para gestionar playlists. Hay que
establecer primero una variable de entorno. Hay un script para hacerlo.
"""

# pylint: disable=import-error
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser


# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
from config import DEVELOPER_KEY
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def youtube_search(options):
    """
    Busca un vídeo según las opciones recibidas.
    """
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)
    if isinstance(options, str):
        qry = options
        search_response = youtube.search().list(q=qry,
                                                part="id,snippet",
                                                maxResults=1).execute()
    else:
        # Call the search.list method to retrieve results matching the
        # specified query term.
        search_response = youtube.search().list(
            qry=options.qry,
            part="id,snippet",
            maxResults=options.max_results).execute()
    videos = []
    channels = []
    playlists = []
    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append((search_result["snippet"]["title"],
                           search_result["id"]["videoId"]))
        elif search_result["id"]["kind"] == "youtube#channel":
            channels.append("%s (%s)" % (search_result["snippet"]["title"],
                                         search_result["id"]["channelId"]))
        elif search_result["id"]["kind"] == "youtube#playlist":
            playlists.append("%s (%s)" % (search_result["snippet"]["title"],
                                          search_result["id"]["playlistId"]))
    return videos

if __name__ == "__main__":
    argparser.add_argument("--q", help="Search term", default="Google")
    argparser.add_argument("--max-results", help="Max results", default=25)
    ARGS = argparser.parse_args()
    try:
        VIDEOS = youtube_search(ARGS)
        print("Videos:\n",
              "\n".join(["{} ({})".format(v[0], v[1]) for v in VIDEOS]),
              "\n")
        # print("Channels:\n", "\n".join(channels), "\n")
        # print("Playlists:\n", "\n".join(playlists), "\n")
    except HttpError as excepcion:
        print("An HTTP error {} occurred:\n{}".format(
            excepcion.resp.status, excepcion.content))
