import os

class SenpaiSong:

    def __init__(self, path, title="No Song Title"):
        '''(SenpaiSong, str, str) -> SenpaiSong
        path: where to find the song. can be https:// or normal path.
        title: title of song.
        '''
        self.path = path
        self.title = title
        self.ref = 1

    def delete_local(self):
        self.ref -= 1
        if (self.ref == 0):
            os.remove(self.path)

    def __str__(self):
        return self.title
