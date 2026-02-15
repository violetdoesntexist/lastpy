
import os
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime


current_directory = os.getcwd()
file_path = current_directory + "/api.txt"
print("The current working directory is:", current_directory)
time.sleep(0.5)
print("checking if onboarding is needed")
entries = os.listdir(current_directory)
print(entries)
if os.path.exists(file_path):
   print("PASS")
   with open("api.txt", "r") as file:
      api = file.read().replace("\n", "")


   time.sleep(0.5)
   with open("username.txt", "r") as file:
      username = file.read().replace("\n", "")

      print("username is:" + username)
      print("api key is:" + api)
      URL = (
         "https://ws.audioscrobbler.com/2.0/"
         f"?method=user.getrecenttracks"
         f"&user={username}"
         f"&api_key={api}"
         f"&limit=1"
         f"&format=xml"
      )
   time.sleep(0.5)
while True:
   cmd = input()
   if cmd == "fm":

      def fetch_xml(url: str) -> str:
         headers = {"User-Agent": "lastfm-terminal-script"}
         r = requests.get(url, headers=headers, timeout=10)
         r.raise_for_status()
         return r.text


   def parse_recent(xml_text: str):
      root = ET.fromstring(xml_text)
      track = root.find(".//track")

      if track is None:
         raise Exception("No track found")

      artist = track.findtext("artist")
      name = track.findtext("name")
      album = track.findtext("album")
      url = track.findtext("url")

      now_playing = track.attrib.get("nowplaying") == "true"

      # timestamp
      date_el = track.find("date")
      played_at = None
      if date_el is not None and date_el.attrib.get("uts"):
         ts = int(date_el.attrib["uts"])
         played_at = datetime.fromtimestamp(ts)

      return {
         "artist": artist,
         "track": name,
         "album": album,
         "url": url,
         "now_playing": now_playing,
         "played_at": played_at,
      }


   def print_terminal_card(data: dict):
      print("──────────────────────────────────────────────")

      if data["now_playing"]:
         print(" NOW PLAYING                                  ")
      else:
         print(" LAST SCROBBLE                                ")

      print("──────────────────────────────────────────────")

      print(f" Artist: {data['artist']}")
      print(f" Track : {data['track']}")
      print(f" Album : {data['album'] or '—'}")

      if not data["now_playing"] and data["played_at"]:
         print(f" Time  : {data['played_at']}")

      print(f" Link  : {data['url']}")
   if __name__ == "__main__":
      xml_data = fetch_xml(URL)
      scrobble = parse_recent(xml_data)
      print_terminal_card(scrobble)

   else:
      print("ONBOARDING NEEDED")
      f = open("api.txt", "x")
      time.sleep(0.5)
      print("please enter your last.fm api key:")
      apiinp = input()
      print("your api key is:", apiinp)
      f1 = open("api.txt", "w")
      f1.write(apiinp)
      f1.close()
      time.sleep(0.5)
      f2 = open("username.txt", "x")
      print("please enter your last.fm username:")
      usernameinp = input()
      print("your username is:", usernameinp)
      f2 = open("username.txt", "w")
      f2.write(usernameinp)
      f2.close()
