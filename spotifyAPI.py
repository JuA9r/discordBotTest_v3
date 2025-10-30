import os
import asyncio
import configparser

# import spotipy module
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import time
import requests
from requests.exceptions import HTTPError

import pandas as pd
from typing import List, Dict, Any


class ConfigManager:
    """
        This class is used to manage the configuration file.
        self.config is a configparser.ConfigParser object.
        self.config contains the configuration information.
        config_file is the path to the configuration file.
        config_file is optional and defaults to "spotifyAPI.ini" if not provided.
    """
    def __init__(self, config_file: str = "spotifyAPI.ini") -> None:

        """Initialize the ConfigManager object."""

        """
        :raises FileNotFoundError: If the config file is not found.
        :raises configparser.Error: If there is an error in the config file.
        :raises KeyError: If the config file does not contain the required information.
        :type config_file: str
        :param config_file: The path to the config file.
        Defaults to "spotifyAPI.ini".
        """

        # create an empty list
        self.ids = []
        self.artists = []
        self.tracks = []
        self.track_list = []

        self.sp: spotipy.Spotify | None = None
        self.results: dict[str, Any] | None = None
        self.id_myList: pd.DataFrame | None = None

        self.config = configparser.ConfigParser()

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file {config_file} not found.")

        self.config.read(config_file)

    def spotify_get_config(self) -> dict[str, str]:

        """Get the client credentials for Spotify API."""

        return {
            "client_id": self.config["SPOTIFY"]["CLIENT_ID"],
            "client_secret": self.config["SPOTIFY"]["CLIENT_SECRET"]
        }

    def set_certification_info(self) -> None:

        """Set the client credentials for Spotify API."""

        # Set credentials
        client_credentials_manager = SpotifyClientCredentials(
            client_id=self.config["SPOTIFY"]["CLIENT_ID"],
            client_secret=self.config["SPOTIFY"]["CLIENT_SECRET"]
        )
        print(f"{client_credentials_manager}\n")

        self.sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        playlist_url = "https://open.spotify.com/playlist/5grpuCKriEOpBQ8hx4wCbx?si=70cd8a40d98f472a"
        playlist_id = playlist_url.split("/")[-1].split("?")[0]

        # Get the list of songs in a playlist
        self.results = self.sp.playlist(playlist_id)
        print(f"{self.results}")

    def insert_music(self) -> None:

        # Store song titles, artist names, and IDs in a list

        for item in self.results["tracks"]["items"]:
            track = item["track"]

            if track and track["id"]:
                self.tracks.append(track["name"])
                self.ids.append(track["id"])
                self.artists.append(", ".join([art["name"] for art in track["artists"]]))

            else:
                track_name = track['name'] if track and 'name' in track else 'Unknown Track'
                print(f"Skipping track (missing ID or track data): {track_name}")

        # Generate data frame
        self.id_myList = pd.DataFrame({
            "Track": self.tracks,
            "Artist": self.artists,
            "ID": self.ids
        })
        self.id_myList.to_csv("id_myList.csv", index=False)

    def data_acquisition(self):

        process_count = 0

        # Get data for 100 songs in the playlist
        for i in range(len(self.ids)):
            while True:
                try:
                    # Store the id in track_id and get the song data
                    track_id = self.id_myList["ID"][i]
                    track = self.sp.audio_features(track_id)
                    break

                except spotipy.client.SpotifyException as err:
                    # # If the Spotify API returns a 429 error (too many requests)
                    if err.http_status == 429:
                        # Get the time to wait before retrying (default is 1 second)
                        retry_after = int(err.headers.get("Retry-After", 1))
                        # Wait for a specified time
                        time.sleep(retry_after)

                    elif err.http_status == 403:
                        print(f"Skipping track (unauthorized): {self.tracks[i]}")
                        track = None
                        break

                    else:
                        print(f"Error: {err}")
                        track = None
                        break

            # Store the acquired music data in a list
            self.track_list.append(track)

        # Convert a list to a dataframe
        df_myList = pd.concat([pd.DataFrame(t) for t in self.track_list], ignore_index=True)
        df_myList.to_csv("df_myList.csv", index=False)

    def __contains__(self, key: str) -> bool:
        return key in self.config["SPOTIFY"]

    def __str__(self):
        return str(self.config)

    def __repr__(self):
        return str(self.config)


if __name__ == "__main__":
    config = ConfigManager()
    config.set_certification_info()
    config.insert_music()
    config.data_acquisition()