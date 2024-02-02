import os
import json
import boto3
import tempfile
import logging
from datetime import datetime, timedelta

class DezSessionInterface(boto3.Session):
    def __init__(self, cache_creds=False, **kwargs):
        super().__init__(**kwargs)
        self.cache_creds = cache_creds
        self.cache_file = os.path.join(
            tempfile.gettempdir(), f"{super().profile_name}_cached_creds.json"
        )
        self.logger = logging.getLogger(__name__)
        self.cached_creds = self._load_cached_creds()

        if not self._are_cached_creds_valid():
            self.logger.info("Fetching new credentials.")
            new_creds = self.get_credentials()
            expiry_time = datetime.utcnow() + timedelta(hours=1)

            if hasattr(new_creds, 'expiry_time'):
                expiry_time = new_creds.expiry_time

            creds_dict = {
                'AccessKeyId': new_creds.access_key,
                'SecretAccessKey': new_creds.secret_key,
                'SessionToken': new_creds.token,
                'SessionExpiryTime': expiry_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            }

            if self.cache_creds:
                self._save_creds_to_cache(creds_dict)

            self.cached_creds = creds_dict

    def _are_cached_creds_valid(self):
        if not self.cached_creds:
            self.logger.info("No cached credentials found.")
            return False

        expiry_time = datetime.strptime(self.cached_creds.get('SessionExpiryTime'), "%Y-%m-%dT%H:%M:%S.%f")

        try:
            # Test the cached credentials by making a simple request to AWS
            sts_client = boto3.client('sts',
                                     aws_access_key_id=self.cached_creds['AccessKeyId'],
                                     aws_secret_access_key=self.cached_creds['SecretAccessKey'],
                                     aws_session_token=self.cached_creds['SessionToken'])
            sts_client.get_caller_identity()
            if expiry_time > datetime.utcnow():
                self.logger.info("Cached credentials are valid.")
                return True
            else:
                self.logger.info("Cached credentials are expired.")
                return False
        except Exception as e:
            self.logger.error(f"Error testing cached credentials: {e}")
            return False

    def _load_cached_creds(self):
        if os.path.isfile(self.cache_file):
            with open(self.cache_file, 'r') as file:
                try:
                    cached_creds = json.load(file)
                    return cached_creds
                except json.JSONDecodeError:
                    self.logger.warning("Failed to decode JSON from cached credentials file.")
        return None

    def _save_creds_to_cache(self, creds):
        with open(self.cache_file, 'w') as file:
            json.dump(creds, file, indent=4)
        self.logger.info(f"Saved credentials to {self.cache_file}")

    def client(self, *args, **kwargs):
        if not self._are_cached_creds_valid():
            self.logger.info("Cached credentials are invalid. Fetching new credentials.")
            new_creds = self.get_credentials()
            expiry_time = datetime.utcnow() + timedelta(hours=1)

            if hasattr(new_creds, 'expiry_time'):
                expiry_time = new_creds.expiry_time

            creds_dict = {
                'AccessKeyId': new_creds.access_key,
                'SecretAccessKey': new_creds.secret_key,
                'SessionToken': new_creds.token,
                'SessionExpiryTime': expiry_time.strftime("%Y-%m-%dT%H:%M:%S.%f")
            }

            if self.cache_creds:
                self._save_creds_to_cache(creds_dict)

            self.cached_creds = creds_dict

        return super().client(*args, **kwargs,
                              aws_access_key_id=self.cached_creds['AccessKeyId'],
                              aws_secret_access_key=self.cached_creds['SecretAccessKey'],
                              aws_session_token=self.cached_creds['SessionToken'])
