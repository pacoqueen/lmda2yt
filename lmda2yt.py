#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sincroniza una lista de youtube con los vídeos de La Musiquita Del Amor de Zim.
"""

import sys
import argparse
from yt_search import youtube_search
import yt_playlist


def parse_cancion(linea):
    """
    Podría usar regex, pero no. Devuelve el número de orden, artista, título,
    fecha y observaciones o None si no es una línea con esa información en el
    fichero (puede ser un texto de Zim u otra cosa).
    """
    res = None
    if linea.count("-") >= 2:
        linea = linea.replace("[[", "").replace("]]", "")   # Para las
        # tags de Zim rollo [[Clara]].
        separador = "["
        if separador not in linea:
            separador = "("
            if separador not in linea:
                separador = "\n"    # No hay comentarios
        try:
            tema, comentarios = linea.split(separador, 1)
            ordinal, artista, cancion = tema.split("- ", 2)
            numero = int(ordinal.replace(".", ""))
            artista = artista.strip()
            cancion = cancion.strip()
            if comentarios:
                try:
                    fecha, observaciones = comentarios.split("-", 1)
                except ValueError:
                    fecha = ""
                    observaciones = comentarios
                fecha = fecha.strip()   # En modo texto. Nada de datetimes.
                observaciones = observaciones.replace("]", "").strip()
            else:
                fecha = None
                observaciones = None
            res = (numero, artista, cancion, fecha, observaciones)
        except ValueError as value_error:
            print("{}: Bad formatted line: {}".format(value_error, linea),
                  file=sys.stderr)
    return res


def parse_canciones(fichero):
    """
    Abre el fichero de entrada (argparser) y devuelve una lista de
    tuplas con el número de orden, artista, canción, fecha y observaciones.
    """
    res = []
    try:
        fin = open(fichero, "r")
    except IOError:
        print("El fichero {} no existe.".format(fichero))
        sys.exit(1)
    else:
        for linea in fin.readlines():
            data_cancion = parse_cancion(linea)
            if data_cancion:
                res.append(data_cancion)
    return res


def search_youtube(artista, cancion):
    """
    Busca en youtube la canción y devuelve el primer vídeo de los resultados.
    """
    query = artista + " " + cancion
    videos = youtube_search(query)
    try:
        res = videos[0]
    except IndexError:
        res = None
    return res


# pylint: disable=too-many-arguments
def update_playlist(playlist_id, numero, video, fecha, observaciones,
                    force=False):
    """
    Obtengo el vídeo que ocupa la posición indicada y, si es diferente al que
    recibo, lo elimino antes de insertar el nuevo.
    Si force es True, elimina siempre el vídeo de la posición actual.
    """
    # TODO: No se va a dar el caso, pero ¿y si meto menos vídeos de los que
    # hay actualmente en la lista? Supongo que debería eliminar el resto...
    video_id = video[1]
    vact_id, vact_plvid = yt_playlist.get_playlistitemid(playlist_id, numero)
    if force or (vact_id and vact_id != video_id):
        # FIXME: Esto no está funcionando. Simplemente agrega los vídeos al
        # final aunque se repitan.
        yt_playlist.remove_video(vact_plvid)
    print("Insertando {}: {} - {} => {}".format(numero, video, fecha,
                                                observaciones))
    yt_playlist.insert_video(playlist_id, video_id, numero, fecha) # ,
                             # observaciones)


def main():
    """
    Lee la lista de canciones del fichero especificado.
    Obtiene la url de un vídeo de youtube de cada una de las canciones leídas.
    Actualiza la playlist de youtube con los vídeos anteriores.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--fichero", "-f",
                        help="Fichero con lista de canciones.",
                        default="lmda.txt")
    parser.add_argument("--nombre", "-n",
                        help="Nombre de la lista de reproducción.",
                        default="La musiquita del amor")
    parser.add_argument("--descripcion", "-d",
                        help="Si la lista no existe, la creará usando esta "
                             "descripción.",
                        default="La musiquita del amor, Clara edition.")
    parser.add_argument("--verbose", "-v",
                        help="Activa modo debug/verbose.",
                        default=False, action="store_true")
    args = parser.parse_args()
    canciones = parse_canciones(args.fichero)
    i = 0   # Hay una errata en la numeración del Zim. Uso mi propio contador.
    playlist_id = yt_playlist.get_playlist(args.nombre, args.descripcion)
    # pylint: disable=unused-variable
    for numero, artista, cancion, fecha, observaciones in canciones:
        video = search_youtube(artista, cancion)
        if video:
            update_playlist(playlist_id, i, video, fecha, observaciones)
            i = i + 1
    if args.verbose:
        debug_output(canciones)


def debug_output(canciones):
    """
    Salida por consola de las canciones reconocidas en Zim para depuración.
    """
    print(canciones)
    for i, cancion in enumerate(canciones):
        print(i, cancion[0], cancion[1], "--", cancion[2])
    print("{} temazos.".format(len(canciones)))


if __name__ == "__main__":
    main()
