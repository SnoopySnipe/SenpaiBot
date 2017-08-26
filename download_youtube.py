from __future__ import unicode_literals
import youtube_dl

download_dir = "/tmp/"
audio_format = "wav"

ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': download_dir + "%(title)s.mp4",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
# for high quality audio in exchange for audio stutters
#       'preferredcodec': 'flac',
        'preferredcodec': audio_format,
        'preferredquality': '192',
    }],
}

def download_song(url):

    ydl = youtube_dl.YoutubeDL(ydl_opts)
    info_dict = ydl.extract_info(url, download=False)
    ydl.download([url])
    video_title = info_dict.get('title', None)
    return video_title

# with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#    ydl.download(['https://www.youtube.com/watch?v=DVHMC2B1WTo'])

