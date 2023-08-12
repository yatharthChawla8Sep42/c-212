import socket
from threading import Thread
import os
import time
from PIL import ImageTk

from tkinter import *
from tkinter import ttk, filedialog
import ftplib
from ftplib import FTP
import ntpath
from pathlib import Path

from playsound import playsound
from pygame import mixer

SERVER = None
IP_ADDRESS = '127.0.0.1'
PORT = 8050
BUFFER_SIZE = 4096

name = None
listbox =  None
infoLabel = None
playButton = None
filePathLabel = None

song_counter = 0
song_selected = None
playtime = 0
pause = False

font = "Calibri"

def play():
  global song_selected, pause
  song_selected = listbox.get(ANCHOR)

  mixer.init()
  mixer.music.load("shared_files/"+song_selected)
  mixer.music.play()
  if(song_selected != ""):
    infoLabel.configure(text="Now Playing: "+song_selected)
    playButton.configure(text="I I", command=pauseANDresume)
  else:
    infoLabel.configure(text="")

def pauseANDresume():
  global playtime, pause
  pause = not pause

  mixer.music.pause()
  if mixer.music.get_pos() != -1:
    if pause:
      # resume
      playButton.configure(text="I I")
      mixer.music.play(start=playtime/1000)
    else:
      # pause
      playButton.configure(text="▶")
      playtime += mixer.music.get_pos()
  else: stop()

def stop():
  global playtime, song_selected
  playtime = 0

  mixer.music.pause()
  infoLabel.configure(text="")
  playButton.configure(text="▶", command=play)

  song_selected = None

def skip(dir):
  global playtime

  try:
    mixer.music.pause()
    if mixer.music.get_pos() != -1:
      if dir:
        # fast-forward
        playtime += mixer.music.get_pos() + 5000
      else:
        # rewind
        playtime += mixer.music.get_pos() - 5000
    

      if(playtime < 0): playtime = 0
      mixer.music.play(start=playtime/1000)
      playButton.configure(text="I I")
    else: stop()
  except: pass

def musicWindow():
  global listbox, infoLabel, playButton
  global song_counter

  window = Tk()
  window.title("Music Window")
  window.geometry("300x300")
  window.configure(bg="#87CEFA")

  selectLabel = Label(window, text="Select Song", bg="#87CEFA", font=(font, 8))
  selectLabel.place(x=2, y=1)

  listbox = Listbox(window, width=39, height=10, activestyle="dotbox", bg="#87CEFA", borderwidth=2, font=(font, 10))
  listbox.place(x=10, y=18)

  for file in os.listdir("shared_files"):
    fileName = os.fsdecode(file)
    listbox.insert(song_counter, fileName)
    song_counter += 1

  scrollbar1 = Scrollbar(listbox)
  scrollbar1.place(relheight=1, relx=1)
  scrollbar1.config(command=listbox.yview)

  playButton = Button(window, text="▶", width=4, bg="#87CEFA", bd=0, font=(font, 20, "bold"), command=play)
  playButton.place(x=85, y=185)

  stopButton = Button(window, text="■", width=4, bg="#87CEFA", bd=0, font=(font, 20), command=stop)
  stopButton.place(x=215, y=185)

  rewindButton = Button(window, text="I🞀🞀", width=4, bg="#87CEFA", bd=0, font=(font, 20), command=lambda: skip(False))
  rewindButton.place(x=20, y=185)

  forwardButton = Button(window, text="🞂🞂I", width=4, bg="#87CEFA", bd=0, font=(font, 20), command=lambda: skip(True))
  forwardButton.place(x=150, y=185)

  uploadButton = Button(window, text="Upload", width=10, bg="#87CEEB", bd=1, font=(font, 10), command=browseFiles)
  uploadButton.place(x=40, y=250)

  downloadButton = Button(window, text="Download", width=10, bg="#87CEEB", bd=1, font=(font, 10), command=download)
  downloadButton.place(x=180, y=250)

  infoLabel = Label(window, text="", bg="#87CEEB", fg="#00F", font=(font, 8))
  infoLabel.place(x=4, y=280)

  window.resizable(False, False)
  window.mainloop()


def browseFiles():
  global song_counter
  try:
    fileName = filedialog.askopenfilename()
    HOSTNAME = '127.0.0.1'
    USERNAME = "lftpd"
    PASSWORD = "lftpd"

    ftp_server = FTP(HOSTNAME, USERNAME, PASSWORD)
    ftp_server.encoding = "utf-8"
    ftp_server.cwd("shared_files")
    fName = ntpath.basename(fileName)
    with open(fileName, "rb") as file:
      ftp_server.storbinary(f"STOR {fName}", file)

    ftp_server.dir()
    ftp_server.quit()

    listbox.insert(song_counter, fName)
    song_counter = song_counter + 1

  except FileNotFoundError:
    print("Cancel Button Pressed")

def download():
  downloadedSong = listbox.get(ANCHOR)
  infoLabel.configure(text="Downloading " + downloadedSong)

  HOSTNAME = '127.0.0.1'
  USERNAME = "lftpd"
  PASSWORD = "lftpd"

  home = str(Path.home())
  downloadPath = home+"/Downloads"
  ftp_server = FTP(HOSTNAME, USERNAME, PASSWORD)
  ftp_server.encoding = "utf-8"
  ftp_server.cwd("shared_files")

  localFileName = os.path.join(downloadPath, downloadedSong)
  file = open(localFileName, "wb")
  ftp_server.retrbinary("RETR " + downloadedSong, file.write)
  ftp_server.dir()
  file.close()
  ftp_server.quit()

  infoLabel.configure(text="Download Complete")
  time.sleep(1)
  if (song_selected != ""):
    infoLabel.configure(text="Now Playing" + song_selected)
  else:
    infoLabel.configure(text="")



def setup():
  global SERVER, IP_ADDRESS, PORT
  SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  SERVER.connect((IP_ADDRESS, PORT))

  musicWindow()

setup()