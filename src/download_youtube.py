from __future__ import unicode_literals
import time

import youtube_dl

import senpai_song

DOWNLOAD_DIR = "/tmp/"
AUDIO_FORMAT = "wav"

_unprocessed_file_path = None

def senpai_progress_hook(progress_info):
    global _unprocessed_file_path
    if (progress_info["status"] == "finished"):
        _unprocessed_file_path = progress_info["filename"]
        print("_unprocessed_file_path: " + _unprocessed_file_path)


def get_song_info(url : str):
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
        song = senpai_song.SenpaiSong()
        song.title = info_dict.get('title', None)
        song.url = url
        song.path = url

    return song

def download_song(url : str):
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

        # actual download
        info_dict = ydl.extract_info(url)

        # create SenpaiSong object
        song = senpai_song.SenpaiSong()
        song.title = info_dict.get('title', None)
        song.url = url

        global _unprocessed_file_path
        while (_unprocessed_file_path is None):
            print("sleeping...")
            time.sleep(1)

        processed_file_path = _unprocessed_file_path
        if (processed_file_path.endswith(".mp4")):
            processed_file_path = processed_file_path[:-3] + AUDIO_FORMAT
        print("song file path: ", processed_file_path)
        song.path = processed_file_path

    return song


def get_download_dir():
    return DOWNLOAD_DIR

def get_audio_format():
    return AUDIO_FORMAT

if (__name__ == "__main__"):
    # with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    dict_ret = download_song('https://www.youtube.com/watch?v=sO_371leHlo')
    print(dict_ret)
