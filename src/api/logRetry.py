import logging
import streamlit as st
from urllib3 import Retry


class LogRetry(Retry):
    """
    Adding extra logs before making a retry request, including backoff details in the sequence.
    """

    def __init__(self, *args, logger_name="LogRetry", **kwargs):
        self.logger = logging.getLogger(logger_name)
        super().__init__(*args, **kwargs)

    def calculate_backoff(self, retry_count):
        """
        Calculate the backoff time for the current retry attempt based on exponential backoff logic.
        """
        # Formula: backoff_factor * (2 ** (retry_count - 1)), where retry_count starts at 1
        return self.backoff_factor * (2 ** (retry_count - 1))

    def increment(self, method=None, url=None, response=None, error=None, _pool=None, _stacktrace=None):
        # Determine the current retry count
        retry_count = len(self.history) + 1

        # Calculate backoff time and the sequence position
        current_backoff = self.calculate_backoff(retry_count)

        # Log the retry information
        if response:
            st.toast(f"Backoff retrying API request... waiting {current_backoff}s", icon="⚠️")
            self.logger.warning(
                f"Retry triggered for {url}. Status: {response.status}. "
                f"Retry {retry_count}: Backoff {current_backoff}s in the sequence."
            )
        elif error:
            self.logger.warning(
                f"Retry triggered for {url}. Error: {error}. "
                f"Retry {retry_count}: Backoff {current_backoff}s in the sequence."
            )

        # Call the parent class's increment method to proceed with the retry logic
        return super().increment(method, url, response, error, _pool, _stacktrace)
