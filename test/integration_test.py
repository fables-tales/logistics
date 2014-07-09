import os
import app
import re
import unittest
import tempfile
import json

class IntegrationTest(unittest.TestCase):

    def setUp(self):
        app.app.config["TESTING"] = True
        self.app = app.app.test_client()

    def test_index_page(self):
        response = self.app.get("/")
        assert "logistics" in response.data.lower()

    def test_puts_zip_in_javascript_when_project_exists(self):
        response = self.do_html_export(self.publicly_clonable_repository())
        assert re.search(self.redirect_to_robot_zip_regex(), response.data)

    def test_shows_success_flash(self):
        response = self.do_html_export(self.publicly_clonable_repository())
        assert re.search("alert-success", response.data)

    def test_shows_failure_flash(self):
        response = self.do_html_export(self.nonexistant_repository())
        assert re.search("alert-danger", response.data)

    def test_removes_export_session_key_on_next_request(self):
        self.do_html_export(self.publicly_clonable_repository())
        response = self.app.get("/")
        assert not re.search(self.redirect_to_robot_zip_regex(), response.data)

    def test_gives_zip_url_when_client_accepts_json(self):
        response = self.do_json_export(self.publicly_clonable_repository())
        assert response.status_code == 200
        assert re.search("/.*/robot.zip", json.loads(response.data)["zip_url"])

    def test_gives_400_with_bad_url_when_client_accepts_json(self):
        response = self.do_json_export(self.nonexistant_repository())
        print response.status_code
        assert response.status_code == 400
        assert json.loads(response.data)["errors"][0] == "EXPORT_FAIL"

    def test_gives_zip_url_when_client_accepts_plaintext(self):
        response = self.do_plaintext_export(self.publicly_clonable_repository())
        assert response.status_code == 200
        assert re.search("/.*/robot.zip", response.data)

    def test_gives_400_with_bad_url_when_client_accepts_plaintext(self):
        response = self.do_plaintext_export(self.nonexistant_repository())
        print response.status_code
        assert response.status_code == 400
        assert "EXPORT_FAIL" in response.data

    def test_cross_origin(self):
        response = self.do_json_export(self.publicly_clonable_repository())
        print response.headers
        assert response.headers["Access-Control-Allow-Origin"] == "*"


    def redirect_to_robot_zip_regex(self):
        return "window.location.replace.*robot.zip"

    def nonexistant_repository(self):
        return "https://bees.com/"

    def publicly_clonable_repository(self):
        return "https://github.com/samphippen/edi"

    def do_html_export(self, git_url):
        return self.do_export(git_url, "text/html")

    def do_json_export(self, git_url):
        return self.do_export(git_url, "application/json")

    def do_plaintext_export(self, git_url):
        return self.do_export(git_url, "text/plain")

    def do_export(self, git_url, accept):
        return self.app.post(
            "/export",
            data={
                "git_url":git_url,
            },
            follow_redirects=True,
            headers=[("Accept", accept)]
        )


if __name__ == "__main__":
    unittest.main()
