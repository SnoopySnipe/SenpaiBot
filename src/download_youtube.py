from __future__ import unicode_literals
import time

import youtube_dl

from senpai_player import SenpaiSongLocal, SenpaiSongYoutube

DOWNLOAD_DIR = "/tmp/"
AUDIO_FORMAT = "wav"

_unprocessed_file_path = None

def senpai_progress_hook(progress_info):
    global _unprocessed_file_path
    if (progress_info["status"] == "finished"):
        _unprocessed_file_path = progress_info["filename"]
        print("_unprocessed_file_path: " + _unprocessed_file_path)


def create_youtube_song(url : str, voice_channel):
    '''(str) -> dict'''
    ydl_pretend_opts = {
        'simulate': True,
        'nooverwrites': True,
        'restrictfilenames': True,
        }

    song = None
    if (url is not None):
        ydl = youtube_dl.YoutubeDL(ydl_pretend_opts)

        ydl.add_progress_hook(senpai_progress_hook)

        # actual download
        info_dict = ydl.extract_info(url)

        # create SenpaiSong object
        song = SenpaiSongYoutube(info_dict.get('title', None),
                                 url, voice_channel)

    return song

def create_local_song(url : str, voice_channel):
    ''' '''

    ydl_download_opts = {
        'format': 'bestaudio/best',
        'outtmpl': DOWNLOAD_DIR + "%(title)s.mp4",
        'restrictfilenames': True,
        'nooverwrites': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
    # for high quality audio in exchange for audio stutters
    #       'preferredcodec': 'flac',
            'preferredcodec': AUDIO_FORMAT,
            'preferredquality': '192',
        }],
    }
    info_dict = None

    song = None
    if (url is not None):
        ydl = youtube_dl.YoutubeDL(ydl_download_opts)

        ydl.add_progress_hook(senpai_progress_hook)

        global _unprocessed_file_path
        _unprocessed_file_path = None

        # actual download
        info_dict = ydl.extract_info(url)

        while (_unprocessed_file_path is None):
            print("sleeping...")
            time.sleep(1)

        processed_file_path = _unprocessed_file_path
        if (processed_file_path.endswith(".mp4")):
            processed_file_path = processed_file_path[:-3] + AUDIO_FORMAT
        print("song file path:", processed_file_path)

        song = SenpaiSongLocal(info_dict.get("title", None), url,
                               processed_file_path, voice_channel)

    return song


def get_download_dir():
    return DOWNLOAD_DIR

def get_audio_format():
    return AUDIO_FORMAT

