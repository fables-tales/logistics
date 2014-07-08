import os
import app
import re
import unittest
import tempfile

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


    def redirect_to_robot_zip_regex(self):
        return "window.location.replace.*robot.zip"

    def nonexistant_repository(self):
        return "https://bees.com/"

    def publicly_clonable_repository(self):
        return "https://github.com/samphippen/nemesis"

    def do_html_export(self, git_url):
        return self.app.post(
            "/export",
            data={
                "git_url":git_url,
            },
            follow_redirects=True,
            headers=[("Accept", "text/html")]
        )


if __name__ == "__main__":
    unittest.main()
