# SenpaiBot

Our bot for our Discord server.

<p>
<img src="https://github.com/SnoopySnipe/SenpaiBot/blob/master/senpai_bot.png" width="350">
Credits: art by <a href="https://www.instagram.com/sen_yomi/?hl=en">Sen_Yomi @IG</a>
</p>



## Requirements
 - python3.5 or higher
 - pip
 - youtube-dl for python
 - discord.py for python (see [here](https://github.com/Rapptz/discord.py) for dependencies)
```
~ $ python3 -m pip install -U --user discord.py[voice]
~ $ python3 -m pip install -U --user youtube-dl
```

## Running
```
~ $ python3 senpai.py -t [discord_bot_token]
```

## Features

### Commands
- !8ball <question> : answers a yes/no question given by a user.
- !coin	: returns heads	or tails
- !guess : game where user guesses a number between 1 and 10
- !play:
   - \<YouTube URL\> : streams the youtube video into the channel the user is currently in.<br>
  if another video is already playing, video will be added to queue.
   - queue: shows the queue of videos
   - skip : skip to next video
   - pause : pause video
   - resume : resume video
   - stop : clears the queue, and leaves the voice channel
   - locally \<YouTube URL\> : pre downloads the youtube video and converts it to a .wav file in an attempt to minimize audio stutter during playback. After download is complete, video will either be played or queued.
   - localqueue: shows the queue of local videos

