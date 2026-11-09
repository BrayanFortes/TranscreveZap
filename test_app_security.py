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
        html = response.get_data(as_text=True)
        self.assertIn('id="privacy-banner"', html)
        self.assertIn('id="btn-accept-privacy"', html)

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

    def test_privacy_policy_page_and_security_headers(self):
        for path in ["/privacidade", "/politica-de-privacidade"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
            self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
            self.assertIn("default-src 'self'", response.headers.get("Content-Security-Policy", ""))
            html = response.get_data(as_text=True)
            self.assertIn("Política de Privacidade", html)
            self.assertIn("LGPD", html)
            self.assertIn("TranscreveZap/issues", html)
            self.assertIn("Resolução CD/ANPD", html)
            self.assertNotIn("@gmail.com", html)

    def test_browser_client_code_does_not_expose_api_keys(self):
        secret_key = "AIzaSySuperSecretBackendKey987654321"
        with patch.dict("os.environ", {"API_KEY": secret_key, "GEMINI_API_KEY": secret_key}):
            with patch("app.get_api_key", return_value=secret_key):
                # Verify HTML responses
                for endpoint in ["/", "/privacidade"]:
                    res = self.client.get(endpoint)
                    self.assertEqual(res.status_code, 200)
                    self.assertNotIn(secret_key, res.get_data(as_text=True))

                # Verify files in templates and whatsapp-extension
                files_to_check = [
                    "templates/index.html",
                    "templates/privacidade.html",
                    "whatsapp-extension/content.js",
                    "whatsapp-extension/service-worker.js",
                    "whatsapp-extension/recorder.js",
                    "whatsapp-extension/manifest.json",
                ]
                for file_path in files_to_check:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        self.assertNotIn(secret_key, content)
                        # Check that no Google AI API key pattern is hardcoded
                        self.assertNotRegex(content, r"AIza[0-9A-Za-z-_]{35}")

    def test_api_error_does_not_leak_api_key_to_browser(self):
        secret_key = "AIzaSySuperSecretBackendKey987654321"
        with patch("app.get_api_key", return_value=secret_key):
            with patch("app.genai.Client") as mock_client_cls:
                mock_client = MagicMock()
                mock_client_cls.return_value = mock_client
                mock_client.models.generate_content.side_effect = Exception(
                    f"401 Request failed with API key {secret_key}: invalid key"
                )

                data = {"audio": (io.BytesIO(b"fake audio data"), "sample.mp3")}
                res = self.client.post("/api/transcrever", data=data, content_type="multipart/form-data")
                self.assertEqual(res.status_code, 502)
                response_json = res.get_json()
                self.assertNotIn(secret_key, response_json.get("error", ""))
                self.assertNotIn(secret_key, res.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
