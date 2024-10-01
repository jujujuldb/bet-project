import json
import logging
import sys
import time
from datetime import datetime

import schedule

from src.data.scrapers.betclic_scraper import BetclicScraper
from src.data.storage.data_storage import DataStorage
from src.utils.config import load_config
from src.utils.email_sender import EmailSender
from src.utils.json_comparator import JsonComparator
from src.utils.logger import setup_logging


def main_task():
    # Load configuration
    config = load_config()

    # Setup logging
    setup_logging(config['logging'])

    logging.info("Task started")

    # Initialize components
    scraper = BetclicScraper(config)
    storage = DataStorage(config)
    email_sender = EmailSender(config['email'])
    json_comparator = JsonComparator()

    try:
        # Fetch match IDs
        match_ids = scraper.get_match_ids()
        logging.info(f"Fetched {len(match_ids)} match IDs")
        match_ids = match_ids

        # Get ace markets data
        new_ace_markets_data = scraper.get_ace_markets(match_ids)
        logging.info(f"Fetched ace markets data for {len(new_ace_markets_data)} matches")

        # Load previous data from file (if exists)
        try:
            with open('previous_ace_markets_data.json', 'r') as f:
                old_ace_markets_data = json.load(f)
        except FileNotFoundError:
            old_ace_markets_data = []

        changes = []

        for new_match_data in new_ace_markets_data:
            try:
                # Save new data to database
                storage.save_match_data(new_match_data)

                # Compare with old data
                old_match_data = next(
                    (match for match in old_ace_markets_data if
                     match.get('match_id') == new_match_data.get('match_id')), None)
                if old_match_data:
                    match_changes = json_comparator.compare_match_data(old_match_data, new_match_data)
                    if match_changes:
                        # Add player names to the change information
                        match_changes['joueur_1'] = new_match_data.get('contestants', {}).get('joueur 1', 'Unknown')
                        match_changes['joueur_2'] = new_match_data.get('contestants', {}).get('joueur 2', 'Unknown')
                        changes.append(match_changes)
            except Exception as e:
                logging.error(f"Error processing match {new_match_data.get('match_id', 'Unknown')}: {str(e)}")
                continue



        # Save new data to file for next comparison
        with open('previous_ace_markets_data.json', 'w') as f:
            json.dump(new_ace_markets_data, f, default=str)  # Use default=str to handle datetime objects

        # Send email if changes detected
        if changes:
            email_content = format_changes_for_email(changes)
            email_sender.send_email("Ace Markets Changes Detected", email_content)
            logging.info("Changes detected and email sent")
        else:
            logging.info("No changes detected")

        for match_data in new_ace_markets_data:
            try:
                match_id = match_data.get('match_id')
                if match_id is not None:
                    odds_changes = storage.get_odds_changes(match_id)
                    latest_odds = storage.get_latest_odds(match_id)
                    if odds_changes:
                        logging.info(f"Odds changes for match {match_id}: {odds_changes}")
                        logging.info(f"Latest odds for match {match_id}: {latest_odds}")
                else:
                    logging.warning(f"Invalid match_id for match: {match_data}")
            except Exception as e:
                logging.error(f"Error processing odds for match {match_data.get('match_id', 'Unknown')}: {str(e)}")
                continue

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
    finally:
        # Close the connection pool
        storage.close_pool()

    logging.info("Task finished")


def log_sample_match_data(sample_match):
    logging.info("Sample match data:")
    logging.info(f"Match ID: {sample_match['match_id']}")
    logging.info(f"Competition: {sample_match['competition']}")
    logging.info(f"Joueur 1: {sample_match['contestants']['joueur 1']}")
    logging.info(f"Joueur 2: {sample_match['contestants']['joueur 2']}")
    logging.info(f"Start time: {sample_match['start_time']}")

    # Log ace market data
    for market_type, selections in sample_match['aces_data'].items():
        logging.info(f"\nMarket: {market_type}")
        for selection in selections:
            logging.info(f"  {selection['name']}: {selection['odds']}")


def format_changes_for_email(changes):
    content = "The following changes were detected in the ace markets:\n\n"
    for change in changes:
        content += f"Match ID: {change['match_id']}\n"
        content += f"Players: {change['joueur_1']} vs {change['joueur_2']}\n"
        for market, market_changes in change['changes'].items():
            content += f"  Market: {market}\n"
            for selection_change in market_changes:
                content += f"    {selection_change['name']}: {selection_change['old_odds']} -> {selection_change['new_odds']}\n"
        content += "\n"
    return content


def run_scheduler():
    schedule.every(10).minutes.do(main_task)

    logging.info(f"[{datetime.now()}] Scheduler started. Running tasks every 10 minutes.")

    last_error_time = None
    error_count = 0
    loop_count = 0

    while True:
        loop_start_time = datetime.now()
        logging.info(f"[{loop_start_time}] Starting loop {loop_count}")

        try:
            schedule.run_pending()

            # Reset error count if no errors for a while
            if last_error_time and (datetime.now() - last_error_time).total_seconds() > 3600:  # 1 hour
                error_count = 0
                last_error_time = None
                logging.info(f"[{datetime.now()}] Error count reset after 1 hour of no errors")

        except Exception as e:
            current_time = datetime.now()
            error_count += 1
            last_error_time = current_time

            logging.error(f"[{current_time}] An error occurred during scheduled task execution: {str(e)}",
                          exc_info=True)

            if error_count > 5:
                logging.critical(
                    f"[{current_time}] Too many errors occurred (Error count: {error_count}). Stopping scheduler.")
                break

            # Calculate sleep time: 1 minute for first error, then exponential backoff
            sleep_time = min(60 * (2 ** (error_count - 1)), 3600)  # Max 1 hour
            logging.info(f"[{current_time}] Waiting for {sleep_time} seconds before next attempt.")
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            logging.info(f"[{datetime.now()}] Scheduler stopped by user.")
            break

        loop_end_time = datetime.now()
        loop_duration = (loop_end_time - loop_start_time).total_seconds()
        logging.info(f"[{loop_end_time}] Loop {loop_count} completed. Duration: {loop_duration} seconds")

        # Flush the logs
        for handler in logging.getLogger().handlers:
            handler.flush()

        sys.stdout.flush()
        sys.stderr.flush()

        loop_count += 1

        # Sleep for the remaining time to complete 10 minutes
        time_to_sleep = max(0, 600 - loop_duration)  # 600 seconds = 10 minutes
        time.sleep(time_to_sleep)

    logging.info(f"[{datetime.now()}] Scheduler stopped.")


if __name__ == "__main__":
    try:
        # Load configuration
        config = load_config()

        # Setup logging
        setup_logging(config['logging'])

        logging.info(f"[{datetime.now()}] Application started")

        main_task()
        run_scheduler()

    except Exception as e:
        logging.critical(f"[{datetime.now()}] An unexpected error occurred in the main application: {str(e)}",
                         exc_info=True)
    finally:
        logging.info(f"[{datetime.now()}] Application finished")
        # Final flush of all logs
        for handler in logging.getLogger().handlers:
            handler.flush()
        sys.stdout.flush()
        sys.stderr.flush()