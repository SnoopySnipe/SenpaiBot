import os

class SenpaiSong:

    def __init__(self, file_path, title):
        self.file_path = file_path
        self.title = title
        self.ref = 1

    def delete_local(self):
        self.ref -= 1
        if (self.ref == 0):
            os.remove(self.file_path)
