from dotenv import load_dotenv
import os
import base64
from requests import post, get, exceptions
import json
import pandas as pd
import os
import sqlite3

class DataAlreadyExistsError(Exception):
    """Raised when data already exists in the database."""
    pass

class ConsumeAPI():
    """Class to consume Spotify API.
    
    Methods:
        get_token: Return the token to access Spotify API.
        get_auth_header: Return the authorization header to access Spotify API.
        search_for_artist: Return the artist id from Spotify API.
        get_artist_info: Return the artist info from Spotify API.
        get_songs_by_artist: Return the songs info from Spotify API.
        dataframe_builder: Build the dataframe with the data from Spotify API.
        get_songs_by_artists: Return the dataframe with the data from Spotify API.
    """
    def __init__(self):
        self.dotenv = load_dotenv()
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.df = pd.DataFrame(columns=[
            "id_artist",
            "query_date",
            "artist_name",
            "followers",
            "artist_popularity",
            "name_song",
            "song_popularity",
            "release_date",
            "album_name",
            "total_tracks"
        ])
          
    def get_token(self) -> str:
        try:
            auth_string = self.client_id + ":" + self.client_secret
            auth_bytes = auth_string.encode("utf-8")
            auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
            url = "https://accounts.spotify.com/api/token"
            headers = {
                "Authorization": "Basic " + auth_base64,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {"grant_type": "client_credentials"}
            result = post(url, headers=headers, data=data)
            result.raise_for_status()
            json_result = json.loads(result.content)
            token = json_result["access_token"]

            return token

        except exceptions.RequestException as e:
            raise  SystemExit(e)

    def get_auth_header(self) -> dict:
        return{"Authorization": "Bearer " + self.get_token()}

    def search_for_artist(self, artist_name:str) -> str:
        try:
            url = "http://api.spotify.com/v1/search"
            headers = self.get_auth_header()
            query = f"?q={artist_name}&type=artist&limit=1"
            query_url = url + query
            result = get(query_url, headers=headers)
            result.raise_for_status()
            json_result = json.loads(result.content)["artists"]["items"]
            
            return json_result[0]["id"]
        
        except exceptions.RequestException as e:
            raise  SystemExit(e)
    
    def get_artist_info(self, artist_id: str) -> dict:
        try:
            url = f"http://api.spotify.com/v1/artists/{artist_id}"
            headers = self.get_auth_header()
            result = get(url, headers=headers)
            result.raise_for_status()
            json_result = json.loads(result.content)
            
            return json_result

        except exceptions.RequestException as e:
            raise  SystemExit(e)

    def get_songs_by_artist(self, artist_id: str, country="BR"):
        try:
            url = f"http://api.spotify.com/v1/artists/{artist_id}/top-tracks?country={country}"
            headers = self.get_auth_header()
            result = get(url, headers=headers)
            result.raise_for_status()
            json_result = json.loads(result.content)["tracks"]
            
            return json_result
        
        except exceptions.RequestException as e:
            raise  SystemExit(e)
    
    def dataframe_builder(self, artist_id: str) -> None:
        artist_info = self.get_artist_info(artist_id)
        songs_info = self.get_songs_by_artist(artist_id)
        query_date = pd.Timestamp.now().strftime("%Y-%m-%d") 
        
        for song in songs_info:
            self.df = self.df._append({
                "id_artist": artist_id,
                "query_date": query_date,
                "artist_name": artist_info["name"],
                "followers": artist_info["followers"]["total"],
                "artist_popularity": artist_info["popularity"],
                "name_song": song["name"],
                "song_popularity": song["popularity"],
                "release_date": song["album"]["release_date"],
                "album_name": song["album"]["name"],
                "total_tracks": song["album"]["total_tracks"]
            }, ignore_index=True)
                   
    def get_songs_by_artists(self, artists_list: list) -> pd.DataFrame:
        for artist in artists_list:
            id_artist = self.search_for_artist(artist)
            self.dataframe_builder(id_artist)
            
        return self.df


class ConnectToSQLite():
    """Class to connect to SQLite database.
    
    Methods:
        check_path: Check if the path exists, if not, create it.
        create_database: Create the database if not exists.
        connect_database: Connect to the database.
    """
    def __init__(self):
        self.database_name = "artists_data.db"
        self.database_file = "sql_files"
        
    def check_path(self, paste:str) -> str:
        path = os.path.join("src", "data_files", paste)

        if not os.path.exists(path):
            os.makedirs(path)
            
        return path
    
    def create_database(self) -> None:
        path = self.check_path(self.database_file)
        full_path = os.path.join(path, self.database_name)
        conn = sqlite3.connect(full_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE artists_data (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                id_artist VARCHAR(255) NOT NULL,
                query_date DATE NOT NULL,
                artist_name VARCHAR(255) NOT NULL,
                followers INTEGER NOT NULL,
                artist_popularity INTEGER NOT NULL,
                name_song VARCHAR(255) NOT NULL,
                song_popularity INTEGER NOT NULL,
                release_date DATE NOT NULL,
                album_name VARCHAR(255) NOT NULL,
                total_tracks INTEGER NOT NULL
            );
        """)
        conn.commit()
        conn.close()
        
    def connect_database(self) -> sqlite3.Connection:
        path = self.check_path(self.database_file)
        full_path = os.path.join(path, self.database_name)
        
        if not os.path.exists(full_path):
            self.create_database()

        conn = sqlite3.connect(full_path)
        
        return conn


class DataExporter():
    """Class to export data from Spotify API.
    
    Methods:
        import_artists_names: Import the artists names from JSON file.
        export_data: Export the data from Spotify API to SQLite database.
    """
    def __init__(self, source=ConsumeAPI(), conn=ConnectToSQLite()):
        self.source = source
        self.conn = conn
    
    def import_artists_names(self) -> list[str]:
        try:
            path = self.conn.check_path("artists_names")
            with open(f"{path}/names.json", "r") as infile:
                names = json.load(infile)
            
            return names
        
        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        
    def export_data(self) -> None:
        name_list = self.import_artists_names()
        df = self.source.get_songs_by_artists(name_list)
        conn = self.conn.connect_database()

        num_duplicates = 0

        try:
            for _, row in df.iterrows():
                if self.check_data_db(conn, pd.DataFrame([row])):
                    num_duplicates += 1

            if num_duplicates > 0:
                raise DataAlreadyExistsError(f"{num_duplicates} rows already exist in the database.")
            else:
                df.to_sql("artists_data", con=conn, if_exists="append", index=False)

        finally:
            conn.close()
        
    def check_data_db(self, conn: sqlite3.Connection, df: pd.DataFrame) -> bool:
        with conn:
            cursor = conn.cursor()

            for _, row in df.iterrows():
                cursor.execute("""
                    SELECT * FROM artists_data
                    WHERE id_artist = ? AND query_date = ? AND name_song = ?
                """, (row["id_artist"], row["query_date"], row["name_song"]))
                
                data = cursor.fetchone()

                if not data:
                    return False  

            return True 


class DataProvider():
    """Class to query data from SQLite database.
    
    Methods:
        getRecentDataByArtist: Return the most recent data from an artist.
        getRecentTopTracksDataByArtist: Return the most recent top tracks data from an artist.
    """
    def __init__(self, source=DataExporter(), conn=ConnectToSQLite()):
        self.source = source
        self.conn = conn
    
    def getRecentDataByArtist(self, artist: str) -> dict:
        conn = self.conn.connect_database()
        with conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM artists_data
                WHERE id_artist = '{artist}'
                OR artist_name = '{artist}'
                ORDER BY query_date DESC
                LIMIT 1;
            """)
            data = cursor.fetchone()
            
            if data:
                dict_result = {
                    "id_artist": data[1],
                    "query_date": data[2],
                    "artist_name": data[3],
                    "followers": data[4],
                    "artist_popularity": data[5]
                }
            else:
                raise ValueError("Artist not found.")
            
            dict_result = {artist: dict_result}
            
            return dict_result
    
    def getRecentTopTracksDataByArtist(self, artist: str) -> list:
        conn = self.conn.connect_database()
        with conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM artists_data
                WHERE id_artist = '{artist}'
                OR artist_name = '{artist}'
                ORDER BY query_date DESC
                LIMIT 10;
            """)
            data = cursor.fetchall()

            tracks_data = []
            if data:
                for track in data:
                    dict_result = {
                        "id_artist": track[1],
                        "query_date": track[2],
                        "name_song": track[6],
                        "song_popularity": track[7],
                        "release_date": track[8],
                        "album_name": track[9],
                        "total_tracks": track[10]
                    }
                    tracks_data.append(dict_result)
            else:
                raise ValueError("Artist not found.")

            dict_result = {artist: tracks_data}
            
            return dict_result
