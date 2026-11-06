import io
import unittest
from unittest.mock import MagicMock, patch

from app import app, SlidingWindowRateLimiter, transcribe_limiter


class SecurityAuditTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        app.config["TESTING"] = True
        # Reset rate limiter storage before each test
        transcribe_limiter.requests.clear()

    def test_security_headers_present_on_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(response.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertIn("Content-Security-Policy", response.headers)
        self.assertIn("default-src 'self'", response.headers.get("Content-Security-Policy"))

    def test_cors_headers_allowed_for_extension_and_local(self):
        headers = {"Origin": "chrome-extension://abcdefghijklmnop"}
        response = self.client.options("/api/transcrever", headers=headers)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "chrome-extension://abcdefghijklmnop")
        self.assertIn("POST", response.headers.get("Access-Control-Allow-Methods", ""))

        # Localhost origin
        response = self.client.options("/api/transcrever", headers={"Origin": "http://localhost:5000"})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers.get("Access-Control-Allow-Origin"), "http://localhost:5000")

    def test_cors_headers_not_granted_to_untrusted_origins(self):
        response = self.client.options("/api/transcrever", headers={"Origin": "https://malicious-site.example.com"})
        self.assertIsNone(response.headers.get("Access-Control-Allow-Origin"))

    def test_rate_limiter_logic(self):
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)
        client_key = "192.168.1.100"

        # 3 requests allowed
        self.assertTrue(limiter.is_allowed(client_key)[0])
        self.assertTrue(limiter.is_allowed(client_key)[0])
        self.assertTrue(limiter.is_allowed(client_key)[0])

        # 4th request blocked
        allowed, retry_after = limiter.is_allowed(client_key)
        self.assertFalse(allowed)
        self.assertGreaterEqual(retry_after, 1)

    def test_rate_limiting_endpoint(self):
        # Configure a small limit for testing
        with patch.object(transcribe_limiter, "max_requests", 2):
            # 1st request (fails on missing API key or audio, but passes rate limiting)
            res1 = self.client.post("/api/transcrever")
            self.assertNotEqual(res1.status_code, 429)

            # 2nd request
            res2 = self.client.post("/api/transcrever")
            self.assertNotEqual(res2.status_code, 429)

            # 3rd request should trigger 429
            res3 = self.client.post("/api/transcrever")
            self.assertEqual(res3.status_code, 429)
            self.assertIn("Muitas solicitações", res3.get_json().get("error", ""))
            self.assertIn("Retry-After", res3.headers)

    def test_empty_audio_rejected(self):
        with patch("app.get_api_key", return_value="test-api-key"):
            data = {"audio": (io.BytesIO(b""), "empty.mp3")}
            response = self.client.post("/api/transcrever", data=data, content_type="multipart/form-data")
            self.assertEqual(response.status_code, 400)
            self.assertIn("vazio", response.get_json().get("error", "").lower())

    def test_unsupported_audio_extension_rejected(self):
        with patch("app.get_api_key", return_value="test-api-key"):
            data = {"audio": (io.BytesIO(b"fake data"), "script.exe")}
            response = self.client.post("/api/transcrever", data=data, content_type="multipart/form-data")
            self.assertEqual(response.status_code, 400)
            self.assertIn("Formato não aceito", response.get_json().get("error", ""))


if __name__ == "__main__":
    unittest.main()
