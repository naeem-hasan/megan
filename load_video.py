import pafy
from PyQt4.QtCore import QThread, SIGNAL


class LoadVideo(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.url = ""

    def __del__(self):
        self.wait()

    def add_url(self, url):
        self.url = url

    def run(self):
        try:
            video = pafy.new(self.url)
            self.emit(SIGNAL("done"), video)
        except:
            self.emit(SIGNAL("error"))


class DownloadVideo(QThread):
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def set_stuff(self, stream, file_name):
        self.stream = stream
        self.file_name = file_name

    def update_progress_bar(self, total, downloaded, ratio, speed, eta):
        self.emit(SIGNAL("progress"), total, downloaded, ratio, speed, eta)

    def run(self):
        self.stream.download(self.file_name, quiet=True, callback=self.update_progress_bar)
        self.emit(SIGNAL("downloaded"))
