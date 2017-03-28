import sys
import res
from load_video import LoadVideo, DownloadVideo
from PyQt4 import QtGui, uic
from PyQt4.QtCore import SIGNAL
from os.path import expanduser, join


def return_list(videos, audios):
    output = []
    for i in videos:
        output.append(i.resolution + " " + i.extension)
    for i in audios:
        output.append(i.bitrate + " " + i.extension)

    return output


class MeganMainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MeganMainWindow, self).__init__()
        uic.loadUi('main.ui', self)

        self.palette = QtGui.QPalette()
        self.palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(QtGui.QPixmap("bg.jpg")))
        self.setPalette(self.palette)

        self.first = True
        self.prog = True
        self.n = 0
        self.allstreams = []
        self.video_stuff.setVisible(False)

        self.load_video_button.clicked.connect(self.on_load)
        self.download_button.clicked.connect(self.download_video)
        self.pushButton.clicked.connect(self.about)
        self.video_url.returnPressed.connect(self.on_load)

        self.load_thread = LoadVideo()
        self.connect(self.load_thread, SIGNAL("done"), self.update_things)
        self.connect(self.load_thread, SIGNAL("error"), self.show_error)

        self.download_thread = DownloadVideo()
        self.connect(self.download_thread, SIGNAL("downloaded"), self.video_downloaded)
        self.connect(self.download_thread, SIGNAL("progress"), self.update_progress)

        self.adjustSize()
        self.show()

    def about(self):
        QtGui.QMessageBox.about(self.main_widget, "About Megan", "Megan<br><br>A simple yet powerful YouTube downloader.\nIt was created to faciliate downloading YouTube videos in various formats.<br>Developer: Naeem Hasan<br><a href='http://naeemhasan.tk'>My website...</a><br><a href='http://www.facebook.com/wizard.naeemhasan'>I am on Facebook...</a>")

    def show_error(self):
        msg = QtGui.QMessageBox(self.main_widget)
        msg.setIcon(QtGui.QMessageBox.Critical)

        msg.setText("Invalid URL or no internet connection!")
        msg.setInformativeText("Please check your internet connection and the URL you provided.")
        msg.setWindowTitle("Error!")
        msg.exec_()

    def on_load(self):
        self.megan_status.showMessage("Video is being loaded...")
        self.load_thread.terminate()
        self.load_thread.add_url(str(self.video_url.text()))
        self.load_thread.start()

    def update_things(self, video):
        if self.first:
            self.video_stuff.setVisible(True)

        self.video_details.setText("Duration: {0} | Total views: {1} | Likes: {2} | Dislikes: {3}".format(video.duration, video.viewcount, video.likes, video.dislikes))
        self.video_title.setText(video.title)
        self.available_formats.clear()
        self.available_formats.addItems(return_list(video.streams, video.audiostreams))
        self.available_formats.insertSeparator(len(video.streams))
        self.allstreams = video.streams + [""] + video.audiostreams
        self.megan_status.showMessage("Video successfully loaded!")
        self.download_progress.setValue(0)
        self.download_progress.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.adjustSize()
        self.center()
        self.first = False

    def download_video(self):
        stream = self.allstreams[self.available_formats.currentIndex()]
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Download', join(expanduser("~"), stream.title + "." + stream.extension), selectedFilter='*.%s' % stream.extension)
        if filename:
            self.download_thread.set_stuff(stream, str(filename))
            self.download_thread.start()
            self.download_button.setEnabled(False)
            self.available_formats.setEnabled(False)
            self.video_url.setEnabled(False)
            self.load_video_button.setEnabled(False)
            self.download_progress.setEnabled(True)
            self.cancel_button.setEnabled(True)

    def update_progress(self, total, downloaded, ratio, speed, eta):
        if self.prog:
            self.download_progress.setMaximum(total)

        self.download_progress.setValue(downloaded)
        if self.n == 15:
            self.megan_status.showMessage("{0}MBs/{1}MBs | {2} KBPS | Approximately {3} seconds remaining".format(downloaded / 1000000, total / 1000000, int(speed), int(eta)))
            self.n = 0
        else:
            self.n += 1
        self.prog = False

    def video_downloaded(self):
        msg = QtGui.QMessageBox(self.main_widget)
        msg.setIcon(QtGui.QMessageBox.Information)

        msg.setText("Video downloaded!")
        msg.setInformativeText("Video successfully downloaded in your desired format. Please check the download directory.")
        msg.setWindowTitle("Success")
        msg.exec_()
        self.download_button.setEnabled(True)
        self.available_formats.setEnabled(True)
        self.video_url.setEnabled(True)
        self.load_video_button.setEnabled(True)
        self.download_progress.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.prog = True
        self.n = 0

    def center(self):
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MeganMainWindow()
    sys.exit(app.exec_())
