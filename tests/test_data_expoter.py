import unittest
from unittest.mock import patch
from src.data_exporter import ConsumeAPI, ConnectToSQLite, DataExporter, DataProvider
import os

class TestConsumeAPI(unittest.TestCase):
    @patch('src.data_exporter.pd.DataFrame')
    @patch('src.data_exporter.load_dotenv')
    def test_init(self, mock_load_dotenv, mock_pd):
        ConsumeAPI()
        mock_load_dotenv.assert_called_once()
        mock_pd.assert_called_once()
    
    @patch('src.data_exporter.json.loads')
    @patch('src.data_exporter.post')
    @patch('src.data_exporter.base64.b64encode')
    def test_get_token(self, mock_b64encode, mock_post, mock_json):
        mock_b64encode.return_value = b'TEST'
        consumeapi = ConsumeAPI()
        consumeapi.get_token()
        mock_b64encode.assert_called_once()
        mock_post.assert_called_once()
        mock_json.assert_called_once()
    
    @patch('src.data_exporter.json.loads')
    @patch('src.data_exporter.post')
    @patch('src.data_exporter.base64.b64encode')
    def test_get_token_raise_exception(self, mock_b64encode, mock_post, mock_json):
        mock_post.side_effect = Exception
        with self.assertRaises(Exception):
            consumeapi = ConsumeAPI()
            consumeapi.get_token()
        
    @patch('src.data_exporter.ConsumeAPI.get_token')
    def test_get_auth_header(self, mock_get_token):
        mock_get_token.return_value = 'TEST'
        consumeapi = ConsumeAPI()
        consumeapi.get_auth_header()
        mock_get_token.assert_called_once()
        self.assertIsInstance(consumeapi.get_auth_header(), dict)
        
    @patch('src.data_exporter.ConsumeAPI.get_auth_header')
    @patch('src.data_exporter.get')
    @patch('src.data_exporter.json.loads')
    def test_search_for_artist(self, mock_json, mock_get, mock_get_auth_header):
        mock_get_auth_header.return_value = 'TEST'
        consumeapi = ConsumeAPI()
        consumeapi.search_for_artist('TESTE')
        mock_get_auth_header.assert_called_once()
        mock_get.assert_called_once()
        mock_json.assert_called_once()
        
    @patch('src.data_exporter.ConsumeAPI.get_auth_header')
    @patch('src.data_exporter.get')
    @patch('src.data_exporter.json.loads')
    def test_search_for_artist_raise_exception(self, mock_json, mock_get, mock_get_auth_header):
        mock_get.side_effect = Exception
        with self.assertRaises(Exception):
            consumeapi = ConsumeAPI()
            consumeapi.search_for_artist('TESTE')
        
    @patch('src.data_exporter.ConsumeAPI.get_auth_header')
    @patch('src.data_exporter.get')
    @patch('src.data_exporter.json.loads')
    def test_get_artist_info(self, mock_json, mock_get, mock_get_auth_header):
        mock_get_auth_header.return_value = 'TEST'
        consumeapi = ConsumeAPI()
        consumeapi.get_artist_info('TESTE')
        mock_get_auth_header.assert_called_once()
        mock_get.assert_called_once()
        mock_json.assert_called_once()
        
    @patch('src.data_exporter.ConsumeAPI.get_auth_header')
    @patch('src.data_exporter.get')
    @patch('src.data_exporter.json.loads')
    def test_get_artist_info(self, mock_json, mock_get, mock_get_auth_header):
        mock_get.side_effect = Exception
        with self.assertRaises(Exception):
            consumeapi = ConsumeAPI()
            consumeapi.get_artist_info('TESTE')
    
    @patch('src.data_exporter.ConsumeAPI.get_auth_header')
    @patch('src.data_exporter.get')
    @patch('src.data_exporter.json.loads')
    def testget_songs_by_artist(self, mock_json, mock_get, mock_get_auth_header):
        mock_get_auth_header.return_value = 'TEST'
        consumeapi = ConsumeAPI()
        consumeapi.get_songs_by_artist('TESTE')
        mock_get_auth_header.assert_called_once()
        mock_get.assert_called_once()
        mock_json.assert_called_once()
        
    @patch('src.data_exporter.ConsumeAPI.search_for_artist')
    @patch('src.data_exporter.ConsumeAPI.dataframe_builder')
    def test_get_songs_by_artists(self, mock_dataframe_builder, mock_search_for_artist):
        mock_search_for_artist.return_value = 'TEST'
        consumeapi = ConsumeAPI()
        consumeapi.get_songs_by_artists(['TEST'])
        mock_search_for_artist.assert_called_once()
        mock_dataframe_builder.assert_called_once()
    
    @patch('src.data_exporter.ConsumeAPI.get_artist_info')
    @patch('src.data_exporter.ConsumeAPI.get_songs_by_artist')
    def test_dataframe_builder(self, mock_get_songs_by_artist, mock_get_artist_info):
        consumeapi = ConsumeAPI()
        consumeapi.dataframe_builder('ACDC')
        mock_get_artist_info.assert_called_once()
        mock_get_songs_by_artist.assert_called_once()


class TesteConnectToSQLite(unittest.TestCase):
    def test_init(self):
        conn = ConnectToSQLite()
        self.assertEqual(conn.database_name, "artists_data.db")
        self.assertEqual(conn.database_file, "sql_files")
        
    def test_check_path(self):
        conn = ConnectToSQLite()
        self.assertEqual(conn.check_path("sql_files"), os.path.join("src", "data_files", "sql_files"))
        
    @patch('src.data_exporter.sqlite3.connect')
    def test_create_database(self, mock_connect):
        conn = ConnectToSQLite()
        conn.create_database()
        mock_connect.assert_called_once()
        
    @patch('src.data_exporter.ConnectToSQLite.check_path')
    @patch('src.data_exporter.os.path.join')
    @patch('src.data_exporter.sqlite3.connect')
    def teste_connect_database(self, mock_connect, mock_join, mock_check_path):
        mock_check_path.return_value = 'TEST'
        conn = ConnectToSQLite()
        conn.connect_database()
        mock_check_path.assert_called_once()
        mock_join.assert_called_once()
        mock_connect.assert_called_once()
        

class TestDataExporter(unittest.TestCase):
    def test_init(self):
        exporter = DataExporter()
        self.assertIsInstance(exporter.source, ConsumeAPI)
        self.assertIsInstance(exporter.conn, ConnectToSQLite)

    @patch('src.data_exporter.ConnectToSQLite.check_path')
    @patch('src.data_exporter.open')
    @patch('src.data_exporter.json.loads')
    def test_import_artists_names(self, mock_json, mock_open, mock_check_path):
        exporter = DataExporter()
        exporter.import_artists_names()
        mock_check_path.assert_called_once()
        mock_open.assert_called_once()
        mock_json.assert_called_once()
        
    @patch('src.data_exporter.DataExporter.import_artists_names')
    @patch('src.data_exporter.ConsumeAPI.get_songs_by_artists')
    @patch('src.data_exporter.ConnectToSQLite.connect_database')
    def test_export_data(self, mock_connect_database, mock_get_songs_by_artists, mock_import_artists_names):
        exporter = DataExporter()
        exporter.export_data()
        mock_import_artists_names.assert_called_once()
        mock_get_songs_by_artists.assert_called_once()
        mock_connect_database.assert_called_once()


class TestDataProvider(unittest.TestCase):
    def test_init(self):
        provider = DataProvider()
        self.assertIsInstance(provider.source, DataExporter)
        self.assertIsInstance(provider.conn, ConnectToSQLite)
        
    @patch('src.data_exporter.ConnectToSQLite.connect_database')
    def test_getRecentDataByArtist(self, mock_connect_database):
        mock_connect_database.cursor.execute.fatchone.return_value = 'TEST'
        provider = DataProvider()
        provider.getRecentDataByArtist('TESTE')
        mock_connect_database.assert_called_once()
    
    @patch('src.data_exporter.ConnectToSQLite.connect_database')
    def getRecentTopTracksDataByArtist(self, mock_connect_database):
        mock_connect_database.cursor.execute.fatchone.return_value = 'TEST'
        provider = DataProvider()
        provider.getRecentTopTracksDataByArtist('TEST')
        mock_connect_database.assert_called_once()
        
    @patch('src.data_exporter.ConnectToSQLite.connect_database')
    def getRecentTopTracksDataByArtist_raise_exception(self, mock_connect_database):
        mock_connect_database.cursor.execute.side_effect = Exception
        with self.assertRaises(Exception):
            provider = DataProvider()
            provider.getRecentTopTracksDataByArtist('TEST')
