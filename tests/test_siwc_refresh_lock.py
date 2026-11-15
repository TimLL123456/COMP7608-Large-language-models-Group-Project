"""Offline SIWC credential refresh tests; no real tokens or network calls."""
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from scr.baselines import siwc_auth


class SIWCConcurrentRefreshTests(unittest.TestCase):
    def test_second_worker_reuses_rotated_token_without_refreshing_twice(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            credentials = home / "credentials.json"
            initial = {
                "client_id": "test-client", "refresh_token": "previous-refresh",
                "access_token": "previous-access", "expires_at": 0,
                "scopes": ["chatgpt.tokens.use.direct"],
            }
            with patch.object(siwc_auth, "HOME", home), \
                 patch.object(siwc_auth, "CREDS", credentials):
                siwc_auth.save_json(credentials, initial)
                fake_result = {
                    "access_token": "rotated-access", "refresh_token": "rotated-refresh",
                    "expires_in": 3600, "scope": "chatgpt.tokens.use.direct",
                }
                with patch.object(siwc_auth, "token_request", return_value=fake_result) as request:
                    worker_one = dict(initial)
                    worker_two = dict(initial)
                    self.assertEqual(siwc_auth.access_token(worker_one), "rotated-access")
                    self.assertEqual(siwc_auth.access_token(worker_two), "rotated-access")
                    self.assertEqual(request.call_count, 1)
                    self.assertEqual(request.call_args.args[0]["refresh_token"],
                                     "previous-refresh")
                self.assertEqual(worker_two["refresh_token"], "rotated-refresh")
                self.assertEqual(siwc_auth.read_json(credentials)["refresh_token"],
                                 "rotated-refresh")
                self.assertTrue((home / "credentials.lock").is_file())

    def test_valid_token_does_not_refresh(self):
        valid = {"access_token": "valid", "expires_at": time.time() + 3000}
        with patch.object(siwc_auth, "token_request") as request:
            self.assertEqual(siwc_auth.access_token(valid), "valid")
            request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
