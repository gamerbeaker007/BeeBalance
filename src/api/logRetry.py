import logging
from urllib3 import Retry

class LogRetry(Retry):
    """
    Adding extra logs before making a retry request
    """

    def __init__(self, *args, logger_name="LogRetry", **kwargs):
        self.logger = logging.getLogger(logger_name)
        super().__init__(*args, **kwargs)

    def increment(self, method=None, url=None, response=None, error=None, _pool=None, _stacktrace=None):
        # Log only when a retry is triggered
        if response:
            self.logger.warning(
                f"Retry triggered for {url}. Status: {response.status}. "
                f"Backoff sequence: {self.backoff_factor}s"
            )
        elif error:
            self.logger.warning(f"Retry triggered for {url}. Error: {error}. Backoff sequence: {self.backoff_factor}s")

        # Call the parent class's increment method to proceed with the retry logic
        return super().increment(method, url, response, error, _pool, _stacktrace)
