all: dependencies

dependencies:
	python3 -m pip install -U youtube-dl
	python3 -m pip install -U requests
	git clone https://github.com/Rapptz/discord.py
	cd discord.py
	git checkout rewrite
	python3 -m pip install -U .[voice]
