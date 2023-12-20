from src.data_exporter import DataExporter, DataProvider, DataAlreadyExistsError
import argparse
import time

def main():
    """Query recent data from artists and top tracks from Spotify API.
    
    Arguments:
        --export_data: Export data from Spotify API.
        --get_artist_data (artist_name OR aritst_id): Return the most recent data from an artist.
        --get_top_tracks_data (artist_name OR aritst_id): Return the most recent data from an artist.
    """
    start_time = time.time()
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--export_data",
        action="store_true",
        help="Export data from Spotify API"
    )
    parser.add_argument(
        "--get_artist_data",
        action="append",
        type=str,
        help="Return the most recent data from an artist"
    )
    parser.add_argument(
        "--get_top_tracks_data",
        action="append",
        type=str,
        help="Return the most recent data from an artist"
    )

    args = parser.parse_args()

    try:
        print('Starting the program...')
        exporter = DataExporter()
        provider = DataProvider()
        
        if args.export_data:
            exporter.export_data()
            print("Data exported successfully!")
            
        elif args.get_artist_data:
            print("Here is the most recent data from the artist:")
            print(60 * "-")
            result = provider.getRecentDataByArtist(args.get_artist_data[0])
            print(result)
            
        elif args.get_top_tracks_data:
            print("Here is the most recent top tracks data from the artist:")
            print(60 * "-")
            result = provider.getRecentTopTracksDataByArtist(args.get_top_tracks_data[0])
            print(result)
            
        else:
            print("No option selected. Please, use --help to see the options.")    
             
    except ValueError as e:
        print(f"ValueError: {e}")
    except DataAlreadyExistsError as e:
        print(f"DataAlreadyExistsError: {e}")
    except SystemExit as e:
        print(f"SystemExit: {e}")
    except Exception as e:
        print(f"Error: {e}")
        
    print(60 * "-")
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nRuntime: {round(total_time, 2)} seconds.")

if __name__ == "__main__":
    main()
