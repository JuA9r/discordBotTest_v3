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


class SpotifyAPIManager:

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

        playlist_url = "https://open.spotify.com/playlist/5grpuCKriEOpBQ8hx4wCbx?si=95e7268ff343492f"
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

        if not self.ids:
            print("No track IDs found. Skipping data acquisition.")
            return

        print("Fetching audio features for all tracks in batches...")
        all_features = []

        for i in range(0, len(self.ids), 100):
            chunk = self.ids[i:i + 100]

            while True:
                try:
                    tracks_features = self.sp.audio_features(tracks=chunk)

                    valid_features = [t for t in tracks_features if t is not None]
                    all_features.extend(valid_features)

                    print(
                        f"Fetched features for batch {i // 100 + 1} ({len(chunk)} \
                        tracks requested, {len(valid_features)} found)"
                    )
                    break

                except spotipy.client.SpotifyException as err:
                    if err.http_status == 429:
                        retry_after = int(err.headers.get("Retry-After", 1))
                        print(f"Rate limit hit. Waiting for {retry_after} seconds...")
                        time.sleep(retry_after)
                    else:
                        print(f"Error fetching features: {err}")
                        break

                except Exception as e:
                    print(f"A non-Spotipy error occurred: {e}")
                    break

        if not all_features:
            print("Could not fetch any valid audio features.")
            return

        df_myList = pd.DataFrame(all_features)
        df_myList.to_csv("df_myList.csv", index=False)
        print(f"Successfully saved {len(all_features)} audio features to df_myList.csv")

    def __contains__(self, key: str) -> bool:
        return key in self.config["SPOTIFY"]

    def __str__(self):
        return str(self.config)

    def __repr__(self):
        return str(self.config)


if __name__ == "__main__":
    spotify_api_manager = SpotifyAPIManager()
    spotify_api_manager.set_certification_info()
    spotify_api_manager.insert_music()
    spotify_api_manager.data_acquisition()