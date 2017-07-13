#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo para gestionar playlists de youtube.
"""

import os
import sys
import httplib2
from apiclient.discovery import build   # pylint: disable=import-error
# from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

DEBUG = False

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
# https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
# https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "lmda_client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

FLOW = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                               message=MISSING_CLIENT_SECRETS_MESSAGE,
                               scope=YOUTUBE_READ_WRITE_SCOPE)

STORAGE = Storage("%s-oauth2.json" % sys.argv[0])
CREDENTIALS = STORAGE.get()

if CREDENTIALS is None or CREDENTIALS.invalid:
    FLAGS = argparser.parse_args()
    CREDENTIALS = run_flow(FLOW, STORAGE, FLAGS)

YOUTUBE = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                http=CREDENTIALS.authorize(httplib2.Http()))


def get_playlist(nombre="La musiquita del amor",
                 descripcion="La musiquita del amor, Clara edition."):
    """
    Si ya existe la lista, devuelve su ID. Si no, la crea usando la
    descripción proporcionada.
    """
    list_response = YOUTUBE.playlists().list(
        part="id,snippet",
        mine=True).execute()
    res = None
    for lista in list_response["items"]:
        if lista["snippet"]["title"] == nombre:
            res = lista["id"]
            break
    if not res:
        res = create_playlist(nombre, descripcion)
    return res


def create_playlist(nombre, descripcion=""):
    """
    This code creates a new private playlist in the authorized user's channel.
    """
    playlists_insert_response = YOUTUBE.playlists().insert(
        part="snippet,status",
        body=dict(snippet=dict(title=nombre,
                               description=descripcion),
                  status=dict(privacyStatus="private"))).execute()
    print("New playlist id: %s" % playlists_insert_response["id"])
    return playlists_insert_response["id"]


def remove_video(playlistvideoid):
    """
    Elimina el vídeo de la lista de reproducción «playlist_id». El parámetro
    «playlistvideoid» es único para el vídeo dentro de la lista y diferente
    del ID único universal del propio vídeo.
    """
    response = YOUTUBE.playlistItems().delete(id=playlistvideoid)
    return response


def get_playlistitemid(playlist_id, numero):
    """
    Devuelve el ID único del vídeo dentro de la lista de reproducción del
    vídeo que ocupa la posición «numero» en la lista «playlist_id».
    El id del vídeo dentro de la playlist es diferente del id único del vídeo.
    Un mismo vídeo puede tener diferentes id dentro de diferentes playlists.
    Devuelve None si la lista no llega hasta la posición «numero».
    """
    playlistvideoid = None
    videoid = None
    snippet = YOUTUBE.playlistItems().list(part="snippet",
                                           playlistId=playlist_id).execute()
    items = snippet["items"]
    for item in items:
        position = item["snippet"]["position"]
        if position == numero:
            videoid = item["snippet"]["resourceId"]["videoId"]
            playlistvideoid = item["id"]
            break
    return videoid, playlistvideoid


def insert_video(playlist_id, video_id, numero=None, fecha=None,
                 observaciones=None):
    """
    Agrega el vídeo a la playlist en la posición indicada o por el final si
    no se especifica.
    """
    # if fecha and observaciones:
    #     notas = "{}: {}".format(fecha, observaciones)
    # elif observaciones:
    #     notas = observaciones
    # elif fecha:
    #     notas = fecha
    # else:
    #     notas = None
    snippet = dict(playlistId=playlist_id,
                   resourceId=dict(videoId=video_id,
                                   kind="youtube#video"))
    body = dict(snippet=snippet)
    if not numero is None:
        snippet["position"] = numero
    # No puedo agregar notas al vídeo de otro.
    # if notas:
    #     content_details = dict(note=notas)
    #     body["contentDetails"] = content_details
    if DEBUG:
        print(playlist_id, video_id, numero, fecha, observaciones, body)
    response = YOUTUBE.playlistItems().insert(part="snippet",
                                              body=body).execute()
    return response
