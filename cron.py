import argparse
from multiprocessing import Process, Queue
from main import RadarFetcher, DatabaseManager

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Capture weather radar images and assemble them into a gif for a list of locations.')
    parser.add_argument('-f', '--frames', type=int, default=10, help='The number of frames to capture for the radar animation.')
    parser.add_argument('-d', '--db-path', type=str, default='radar_images.db', help='The path to the SQLite database file to use for storing radar images.')
    args = parser.parse_args()

    locations = {
        'Calgary': 1,
        'Vancouver': 1,
        'Powell River': 2,
        'Miami, Florida': 2,
        'Revelstoke': 2,
        'Alberta': -1,
        'British Columbia': -1
    }

    db_manager = DatabaseManager(args.db_path)
    db_manager.start()

    fetchers = []
    fetcher_processes = []
    for location in locations:
        fetcher = RadarFetcher(location, zoom=locations[location], frames=args.frames, db_queue=db_manager.queue)
        fetchers.append(fetcher)
        fetcher_process = Process(target=fetcher.capture_radar, args=(True,))
        fetcher_process.start()
        fetcher_processes.append(fetcher_process)

    for fetcher_process in fetcher_processes:
        fetcher_process.join()

    db_manager.stop()