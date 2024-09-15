import logging
from apscheduler.schedulers.background import BackgroundScheduler
from betclic.scraper import fetch_data
from betclic.data import DataManager
from betclic.analysis import make_decisions

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    """Main function to run the scraping and decision-making process."""
    data_manager = DataManager()

    # Initial data fetch
    initial_data = fetch_data()
    if initial_
        data_manager.store_data(initial_data)

    # Schedule data fetching and processing
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_data_pipeline, 'interval', minutes=5, args=[data_manager])
    scheduler.start()

    # Keep the script running
    try:
        while True:
            pass  # You can add other tasks here if needed
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

def run_data_pipeline(data_manager: DataManager):
    """Fetches, compares, and makes decisions based on new data."""
    new_data = fetch_data()
    if new_
        changes = data_manager.compare_data(new_data)
        if changes:
            make_decisions(changes)
        data_manager.store_data(new_data)

if __name__ == "__main__":
    main()
