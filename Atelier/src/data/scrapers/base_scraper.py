from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    def get_match_ids(self):
        pass

    @abstractmethod
    def get_match_details(self, match_id):
        pass

    @abstractmethod
    def get_ace_markets(self, match_ids):
        pass