class SenpaiSong:

    def __init__(self):
        '''(SenpaiSong, str, str) -> SenpaiSong
        path: where to find the song. can be https:// or normal path.
        title: title of song.
        '''
        self.url = None
        self.path = None
        self.title = None

    def __str__(self):
        return self.title
