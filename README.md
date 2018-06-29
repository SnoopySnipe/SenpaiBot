# SenpaiBot

Our bot for our Discord server.

<p>
<img src="https://gitlab.com/Kamiyaa/SenpaiBot/raw/master/senpai_bot.png" width="350">
</p>

Credits: art by [Sen_Yomi](https://www.instagram.com/sen_yomi/?hl=en)




## Requirements
 - python3.5.2 or higher
 - pip
  - [requests](http://docs.python-requests.org/en/master/)
  - [youtube-dl](https://github.com/rg3/youtube-dl)
  - discord.py rewrite for python (see [here](https://github.com/Rapptz/discord.py/tree/rewrite) for dependencies)
 - ffmpeg
  - must be in class path
```
~ $ python3 -m pip install -U discord.py[voice]
~ $ python3 -m pip install -U youtube-dl
~ $ python3 -m pip install -U requests
```

## Running
```
~ $ python3 senpai.py -t [discord_bot_token]
```

## Features

### Commands
** all commands must prefix with !senpai **
```
!senpai
  8ball <question> : answers a yes/no question
  coin	: returns heads	or tails
  guess : game where user guesses a number between 1 and 10
  fortune : shows a fortune

  play <Youtube URL>: download and play a YouTube video into the user's voice channel
     if another video is already playing, it will be added to queue
  pause : pause video
  queue: shows the queue of videos
  repeat <on\off> : turn repeat on or off
  resume : resume video
  skip : skip to next video
  stop : clears the queue, and leaves the voice channel

  playstream <YouTube URL> : stream and play a YouTube video into the user's voice channel

  drop/wherewedroppingbois : shows the next location to drop on Fortnite

  codex <entry> : shows the description of a entry in the Warframe wikia codex as well as an visual image of it

  daily <imageboard> : grabs the latest post/image from a supported image board
    <no arguments> : grabs the latest image from a random supported image board
    all : grabs the latest image from all supported image boards
    danbooru : grabs the latest image from danbooru
    gelbooru : ^ but for gelbooru
    konachan : ..
    safebooru : ..
    yandere : ..
```

