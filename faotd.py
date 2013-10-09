#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## Author: Daniel Rode
## Name: FAOTD (Free App of The Day Informer)
## Dependencies: main:{pyside, python3}, fedora:{pyside (get with pip)}
## Version: 4.1
## Made: August 24 2012
## Last updated: September 12 2013


###########
## SETUP ##
###########
# Import
import re, sys, time, webbrowser, platform, tempfile, html
from sys import exit
from urllib.request import urlopen, Request as request
from subprocess import Popen
from optparse import OptionParser
from PySide import QtCore, QtGui as qt

# Variables
tmp = tempfile.gettempdir()
os = platform.system()

# Exceptions
class FetchingDataError(Exception):
    pass

# Parse Options
parser = OptionParser()
parser.add_option("--window-debug", action="store_true", dest="window_debug", default=False,
    help="Turn on window debugging")

if len(sys.argv) > 1 and sys.argv[1] == '?':
    parser.print_help()
    exit()
(options, args) = parser.parse_args()
o = options


############
## Engine ##
############
def core_engine():
    global appi, stars, app_page, app_desc_img, app_banner_img
    # Get Webpage
    print("Retrieving data from the web...")
    for count in range(5):
        try:
            headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36"}
            req = request("http://www.amazon.com/mobile-apps/b?ie=UTF8&node=2350149011", None, headers)
            html = urlopen(req).read()
            faotd_page = html.decode("utf-8", 'ignore')  # convert byte string to unicode string. The "ignore" argument makes the convertor skip over any character that it fails to decode rather than raise an exception
        except:
            if not count == 0:
                print('\r', end="")
            print("trying again...(1.{})".format((count + 1)), end="")
            sys.stdout.flush()
        else:
            if count > 0:
                print()
            break
    else:
        print()
        raise FetchingDataError("Failed to get webpage. Exiting...")

    try:
        # Parse webpage for needed links
        app_page = 'http://www.amazon.com' + re.search(r"(fad-widget-app-name'>[^>]*)", faotd_page).groups()[0].split("='")[1].strip("'")
        banner_img_url = re.search(r"(src='http://g-ecx.images-amazon.com/images/G/01/mas/retail/faad[^']*)", faotd_page).group()[5:]

        # Parse webpage for App Info
        appi = {}
        appi['name'] = re.search("""fad-widget-app-name'>[^>]*>([^<]*)""", faotd_page).groups()[0]
        appi['desc'] = re.search(r'''"fad-widget-description">\n *(.*)\n *</p>''', faotd_page).groups()[0]
        appi['vendor'] = re.search(r""""fad-widget-by-line">\n *by (.*)\n *</div>""", faotd_page).groups()[0]
        appi['rating'] = re.search("""alt="([^ ]* out of 5 stars)""", faotd_page).groups()[0]
    except AttributeError:
        raise #V^#
        raise FetchingDataError("Unable to parse webpage, site must have updated")


    # Get App Banner image
    app_banner_img = (tmp + '/faotd_banner_image')
    ## Retrieve image from web
    for count in range(5):
        try:
            web_banner_img = urlopen(banner_img_url).read()
        except:
            if not count == 0:
                print('\r', end="")
            print("trying again...(3.{})".format((count + 1)), end="")
            sys.stdout.flush()
        else:
            if count > 0:
                print()
            break
    else:
        print()
        raise FetchingDataError("Failed to get image. Exiting...")

    ## Save image to temp folder
    with open(app_banner_img, 'wb') as img:
        img.write(web_banner_img)

    # Calculating stars
    point = int(appi['rating'][2])
    if point in [0, 1, 2]:
        point = 0
    elif point in [3, 4, 5, 6, 7]:
        point = 1
    elif point in [8, 9]:
        point = 2

    stars = []
    for i in range(int(appi['rating'][0])):
        stars.append(2)
    stars.append(point)
    for i in range((5 - len(stars))):
        stars.append(0)

def run_core_engine(self):
    try:
        if o.window_debug:
            time.sleep(0.8)
        else:
            core_engine()
        c.switchToMain.emit()
    except FetchingDataError as e:
        error_message = str(e)
        print("Error:", error_message)
        if error_message == "Unable to parse webpage, site must have updated":
            errorMessage = error_message
        else:
            errorMessage = "Failed to get data from web!"

        c.errorMessage = errorMessage
        c.getDataFail.emit()

def openwebpage():
    print("Opening webpage...")
    webbrowser.open(app_page)
    exit()

class CoreThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
    def run(self):
        run_core_engine(self)

#########
## GUI ##
#########
class GettingInfoScreen(qt.QWidget):
    def __init__(self):
        qt.QWidget.__init__(self, None)

        # Boxes
        vbox = qt.QVBoxLayout()

        # Label
        text = qt.QLabel("<b><big>Retrieving Data...</big></b>")

        # Busy indicator
        self.busyIndicator = qt.QProgressBar()
        self.busyIndicator.setTextVisible(False)
        self.busyIndicator.setRange(0, 0)  # makes it a busy indicator rather than a indicator of how much "progress" has been achieved
        self.busyIndicator.setMinimumWidth(250)

        # Pack
        vbox.addWidget(text, 0, 4)  # last parameter is alignment. 4 apparently means center.
        vbox.addWidget(self.busyIndicator, 0, 4)

        self.setLayout(vbox)


class TheMainScreen(qt.QWidget):
    def __init__(self):
        qt.QWidget.__init__(self, None)

        ## Buttons
        self.yesButton = qt.QPushButton("Yes")
        QtCore.QObject.connect(self.yesButton, QtCore.SIGNAL("clicked()"), openwebpage)
        self.yesButton.setMinimumSize(75, 30)

        self.noButton = qt.QPushButton("No")
        QtCore.QObject.connect(self.noButton, QtCore.SIGNAL("clicked()"), exit)
        self.noButton.setMinimumSize(75, 30)

        ## Lines
        line = qt.QFrame()
        line.setFrameShape(line.HLine)
        line.setFrameShadow(line.Shadow.Sunken)

        ## Text
        text_question = qt.QLabel("Do you want to open the apps page in a web browser?")

        ### App Info
        text_name  = qt.QLabel("<b><i>Today's free app is:  </i></b>")
        text_by    = qt.QLabel("<b><i>By:  </i></b>")
        text_rated = qt.QLabel("<b><i>Rated:  </i></b>")
        text_desc  = qt.QLabel("<b><i>Description:  </i></b>")
        text_desc.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)

        text_name_next  = qt.QLabel(appi['name'])
        text_by_next    = qt.QLabel(appi['vendor'])
        text_desc_next  = qt.QLabel(appi['desc'])
        text_desc_next.setWordWrap(True)

        ## Images
        ### App Banner (will be on top)
        img_banner = qt.QLabel()
        img_banner.setPixmap(qt.QPixmap(app_banner_img))

        ### Stars
        null_star_img = 'images/Null Star.png'
        half_star_img = 'images/Half Star.png'
        full_star_img = 'images/Full Star.png'
        img_stars = []
        for i in range(5):
            if stars[i] == 0:
                star_img = null_star_img
            elif stars[i] == 1:
                star_img = half_star_img
            else:
                star_img = full_star_img
            star_img = qt.QPixmap(star_img)
            star_img = star_img.scaled(12, 12, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
            aLabel = qt.QLabel()
            aLabel.setPixmap(star_img)
            img_stars.append(aLabel)

        ## Sizing
        ### Define Boxes
        vbox = qt.QVBoxLayout()
        hbox = qt.QHBoxLayout()
        text1 = qt.QHBoxLayout()
        text2 = qt.QHBoxLayout()
        text3 = qt.QHBoxLayout()
        rating_hbox = qt.QHBoxLayout()
        questionSizer = qt.QHBoxLayout()

        ### Add to Boxes
        rating_hbox.addWidget(text_rated)
        for i in range(5):
            rating_hbox.addWidget(img_stars[i])
        rating_hbox.addStretch()

        #### Set up text box
        text1.addWidget(text_name)
        text1.addWidget(text_name_next)
        text1.addStretch()
        text2.addWidget(text_by)
        text2.addWidget(text_by_next)
        text2.addStretch()
        text3.addWidget(text_desc)
        text3.addWidget(text_desc_next)

        #### Add to main virtical box
        vbox.addWidget(img_banner, 0, 4)
        vbox.addLayout(text1)
        vbox.addLayout(text2)
        vbox.addLayout(rating_hbox)
        vbox.addLayout(text3)
        vbox.addStretch()

        vbox.addWidget(line, QtCore.Qt.AlignBottom)
        questionSizer.addWidget(text_question)
        questionSizer.addStretch()
        questionSizer.addWidget(self.yesButton)
        questionSizer.addWidget(self.noButton)
        vbox.addLayout(questionSizer)

        hbox.addLayout(vbox)

        ### Set Boxes
        self.hbox = hbox
        self.setLayout(self.hbox)

# Main Window
class Communicate(QtCore.QObject):
    getDataFail = QtCore.Signal()
    switchToMain = QtCore.Signal()

class Window(qt.QMainWindow):
    def __init__(self):
        ## Setup Main Window
        qt.QMainWindow.__init__(self, None)
        self.setWindowTitle("Free App of The Day")
        self.setFixedSize(275, 120)

        ## Show the waiting screen
        self.gettingInfoScreen = GettingInfoScreen()
        self.setCentralWidget(self.gettingInfoScreen)

        c.getDataFail.connect(self.failDialog)
        c.switchToMain.connect(self.switchToMainScreen)

    def switchToMainScreen(self):
        print("Displaying information in window")
        self.theMainScreen = TheMainScreen()
        self.setCentralWidget(self.theMainScreen)
        self.setMaximumSize(999999, 999999)  # Makes it so window can resize again, but doesn't seem proper to me, should be infinate instead of a fixed number even if that number is large
        self.setMinimumSize(500, 450)
        self.resize(self.theMainScreen.sizeHint())
        self.theMainScreen.noButton.setFocus()

    def failDialog(self):
        errorMessage = c.errorMessage
        qt.QMessageBox.critical(self,
            "Error",
            errorMessage)
        exit(2)

################
## The Action ##
################
# If Window Debugging is on, preset data
if o.window_debug:
    ## Window debugger...
    appi = {
    'name':"Really long app Name",
    "vendor":'App Makers®',
    'rating':'1 out of 5 stars',
    'desc':'This app is like really totally cool a lot for all of the a lot people of this world! It can do nothing! Ever found an app that can do that?! We are the best. Pay for our app and we give 0.00001% of it away to poor poor people! Buy this app and you will be changing lives?'
    }
    stars = [2,2,2,1,0]
    app_banner_img = 'images/dev_faotd_banner_image.png'
    app_page = 'http://www.amazon.com/mobile-apps/b?ie=UTF8&node=2350149011'

# Main: Display Window and Run Core
def main():
    global app, c, core_thread, window

    app = qt.QApplication([])
    c = Communicate()

    core_thread = CoreThread()

    window = Window()
    window.show()

    core_thread.start()
    app.exec_()

if __name__ == "__main__":
    main()
