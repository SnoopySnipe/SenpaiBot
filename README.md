# SenpaiBot

Our bot for our Discord server.

<p>
<img src="https://gitlab.com/Kamiyaa/SenpaiBot/raw/master/senpai_bot.png" width="350">
</p>

Credits: art by [Sen_Yomi](https://www.instagram.com/sen_yomi/?hl=en)




## Requirements
 - python3.5 or higher
 - pip
 - [requests](http://docs.python-requests.org/en/master/)
 - [youtube-dl](https://github.com/rg3/youtube-dl)
 - discord.py for python (see [here](https://github.com/Rapptz/discord.py) for dependencies)
```
~ $ python3 -m pip install -U --user discord.py[voice]
~ $ python3 -m pip install -U --user youtube-dl
~ $ python3 -m pip install -U --user requests
```

## Running
```
~ $ python3 senpai.py -t [discord_bot_token]
```

## Features

### Commands
** all commands must prefix with !senpai **
- !8ball <question> : answers a yes/no question given by a user.
- coin	: returns heads	or tails
- guess : game where user guesses a number between 1 and 10
- daily <imageboard> : grabs the latest post/image from a supporting image board.
    currently supports: danbooru, yandere, konachan and gelbooru.
- play:
   - \<YouTube URL\> : streams the youtube video into the channel the user is currently in.<br>
  if another video is already playing, video will be added to queue.
- queue: shows the queue of videos
- skip : skip to next video
- pause : pause video
- resume : resume video
- stop : clears the queue, and leaves the voice channel
- playlocal \<YouTube URL\> : pre downloads the youtube video and converts it to a .wav file in an attempt to minimize audio stutter during playback. After download is complete, video will either be played or queued.
- localqueue: shows the queue of local videos

