import os
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import art
from art import text2art
import colorama
from colorama import init, Fore, Back, Style

init(autoreset=True)
head=text2art("LASTPY")
current_directory = os.getcwd()
file_path = current_directory + "/api.txt"
print(Style.BRIGHT + Fore.RED + head)
time.sleep(0.5)
print("checking if onboarding is needed")
entries = os.listdir(current_directory)
print(entries)

api = None
username = None
URL = None

if os.path.exists(file_path):
    print("PASS")
    with open("api.txt", "r") as file:
        api = file.read().replace("\n", "")

    time.sleep(0.5)
    with open("username.txt", "r") as file:
        username = file.read().replace("\n", "")
    
    print("username is:" + username)
    print("api key is:" + api)
    userart=text2art("hi" + " " + username + "!")
    print(Style.BRIGHT + Fore.RED + userart)
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

    api = apiinp
    username = usernameinp


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


def build_topartists_url(username: str, api: str, period: str, limit: int) -> str:
    return (
        "https://ws.audioscrobbler.com/2.0/"
        f"?method=user.gettopartists"
        f"&user={username}"
        f"&api_key={api}"
        f"&period={period}"
        f"&limit={limit}"
        f"&format=xml"
    )


def build_toptracks_url(username: str, api: str, period: str, limit: int) -> str:
    return (
        "https://ws.audioscrobbler.com/2.0/"
        f"?method=user.gettoptracks"
        f"&user={username}"
        f"&api_key={api}"
        f"&period={period}"
        f"&limit={limit}"
        f"&format=xml"
    )


def raise_if_lastfm_error(xml_text: str):
    root = ET.fromstring(xml_text)
    if root.tag == "lfm" and root.attrib.get("status") == "failed":
        err = root.find("error")
        code = err.attrib.get("code") if err is not None else "?"
        msg = (err.text or "Unknown error").strip() if err is not None else "Unknown error"
        raise Exception(f"Last.fm API error {code}: {msg}")


def parse_top_artists(xml_text: str):
    root = ET.fromstring(xml_text)
    artists = []

    for i, artist_el in enumerate(root.findall(".//artist"), start=1):
        name = artist_el.findtext("name") or ""
        playcount_text = artist_el.findtext("playcount") or "0"
        playcount = int(playcount_text) if playcount_text.isdigit() else 0
        url = artist_el.findtext("url")

        artists.append({
            "rank": i,
            "artist": name.strip(),
            "playcount": playcount,
            "url": (url or "").strip()
        })

    return artists


def parse_top_tracks(xml_text: str):
    root = ET.fromstring(xml_text)
    tracks = []

    for i, track_el in enumerate(root.findall(".//track"), start=1):
        name = (track_el.findtext("name") or "").strip()
        artist = (track_el.findtext("artist/name") or track_el.findtext("artist") or "").strip()
        playcount_text = track_el.findtext("playcount") or "0"
        playcount = int(playcount_text) if playcount_text.isdigit() else 0
        url = (track_el.findtext("url") or "").strip()

        tracks.append({
            "rank": i,
            "track": name,
            "artist": artist,
            "playcount": playcount,
            "url": url
        })

    return tracks


def print_top_tracks(tracks):
    print("\nTop Tracks\n")
    print("┌────┬──────────────────────────────┬────────┐")
    print("│ #  │ Track                        │ Plays  │")
    print("├────┼──────────────────────────────┼────────┤")

    for t in tracks:
        name = (t["track"] or "")[:28]
        print(f"│ {t['rank']:<2} │ {name:<28} │ {t['playcount']:<6} │")

    print("└────┴──────────────────────────────┴────────┘")


def print_top_artists(artists):
    print("\nTop Artists\n")
    print("┌────┬──────────────────────────────┬────────┐")
    print("│ #  │ Artist                       │ Plays  │")
    print("├────┼──────────────────────────────┼────────┤")

    for a in artists:
        name = a["artist"][:28]
        print(f"│ {a['rank']:<2} │ {name:<28} │ {a['playcount']:<6} │")

    print("└────┴──────────────────────────────┴────────┘")


def build_recenttracks_url(username: str, api: str) -> str:
    return (
        "https://ws.audioscrobbler.com/2.0/"
        f"?method=user.getrecenttracks"
        f"&user={username}"
        f"&api_key={api}"
        f"&limit=1"
        f"&format=xml"
    )


while True:
    cmd = input()

    if cmd == "fm":
        URL = build_recenttracks_url(username, api)
        xml_data = fetch_xml(URL)
        scrobble = parse_recent(xml_data)
        print_terminal_card(scrobble)

    if cmd.startswith("ta"):
        parts = cmd.split()

        period = "overall"
        limit = 10

        valid_periods = {"overall", "7day", "1month", "3month", "6month", "12month"}

        if len(parts) >= 2:
            p = parts[1].strip().lower()

            aliases = {
                "7days": "7day",
                "week": "7day",
                "month": "1month",
                "year": "12month",
                "all": "overall",
                "alltime": "overall",
            }
            p = aliases.get(p, p)

            if p in valid_periods:
                period = p
            else:
                print(f"Invalid period '{parts[1]}'. Using default '{period}'.")
                print("Valid periods:", ", ".join(sorted(valid_periods)))

        if len(parts) >= 3:
            if parts[2].isdigit():
                limit = int(parts[2])
            else:
                print(f"Invalid limit '{parts[2]}'. Using default {limit}.")

        top_url = build_topartists_url(username, api, period, limit)
        top_xml = fetch_xml(top_url)
        raise_if_lastfm_error(top_xml)
        artists = parse_top_artists(top_xml)
        print_top_artists(artists)

    if cmd.startswith("tt"):
        parts = cmd.split()

        period = "overall"
        limit = 10

        valid_periods = {"overall", "7day", "1month", "3month", "6month", "12month"}

        if len(parts) >= 2:
            p = parts[1].strip().lower()

            aliases = {
                "7days": "7day",
                "week": "7day",
                "month": "1month",
                "year": "12month",
                "all": "overall",
                "alltime": "overall",
            }
            p = aliases.get(p, p)

            if p in valid_periods:
                period = p
            else:
                print(f"Invalid period '{parts[1]}'. Using default '{period}'.")
                print("Valid periods:", ", ".join(sorted(valid_periods)))

        if len(parts) >= 3:
            if parts[2].isdigit():
                limit = int(parts[2])
            else:
                print(f"Invalid limit '{parts[2]}'. Using default {limit}.")

        top_url = build_toptracks_url(username, api, period, limit)
        top_xml = fetch_xml(top_url)
        raise_if_lastfm_error(top_xml)
        tracks = parse_top_tracks(top_xml)
        print_top_tracks(tracks)