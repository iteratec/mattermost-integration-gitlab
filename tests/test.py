#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Future imports
from __future__ import unicode_literals, absolute_import, print_function

# Python System imports
import os
import unittest
import json
import codecs

# Third-party imports

from mattermost_gitlab.mock_http import MockHttpServerMixin, get_available_port
from mattermost_gitlab import server


def relative_path(name):
    return os.path.join(os.path.dirname(__file__), "data", name)


def file_content(name):
    with codecs.open(relative_path(name), encoding='utf-8') as fp:
        return fp.read()


class FlaskMixin(unittest.TestCase):

    def setUp(self):
        super(FlaskMixin, self).setUp()
        self.app = server.app.test_client()


class BaseTest(FlaskMixin):

    def test_root(self):
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_get(self):
        resp = self.app.get('/new_event')
        self.assertEqual(resp.status_code, 405)


class ServerTestMixin(MockHttpServerMixin, FlaskMixin):

    port = get_available_port()
    url = "/new_event?mattermost_webhook_url=http://127.0.0.1:{}".format(port)

    def setUp(self):
        super(ServerTestMixin, self).setUp()

        _, _, options = server.parse_args(["--tag", "--push"])
        server.app.config.update(options)

    def post(self, name):
        return self.app.post(self.url, data=file_content(name), content_type='application/json')

    def assertGitlabHookWorks(self, name):

        gitlab_json_path = name + ".json"

        resp = self.post(gitlab_json_path)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, b"OK")

    def assertResponse(self, name):

        self.assertGitlabHookWorks(name)

        self.assertEqual(len(self.server.httpd.received_requests), 1)

        mattermost_markdown_path = name + ".md"
        mattermost_data = json.loads(self.server.httpd.received_requests[0]["post"].decode())
        self.assertEqual(set(mattermost_data.keys()), {'username', 'text', 'icon_url'})

        self.maxDiff = 1600
        self.assertMultiLineEqual(mattermost_data["text"], file_content(mattermost_markdown_path))

    def assertResponseNotSent(self, name):
        self.assertGitlabHookWorks(name)
        self.assertEqual(len(self.server.httpd.received_requests), 0)


class IssueTest(ServerTestMixin):

    def test_open(self):
        self.assertResponse("gitlab/issue/open_issue")

    def test_update(self):
        self.assertResponseNotSent("gitlab/issue/update_issue")

    def test_close(self):
        self.assertResponse("gitlab/issue/close_issue")

    def test_reopen(self):
        self.assertResponse("gitlab/issue/reopen_issue")


class MergeRequestTest(ServerTestMixin):

    def test_open(self):
        self.assertResponse("gitlab/merge_request/open_merge_request")

    def test_update(self):
        self.assertResponse("gitlab/merge_request/update_merge_request")

    def test_close(self):
        self.assertResponse("gitlab/merge_request/close_merge_request")

    def test_reopen(self):
        self.assertResponse("gitlab/merge_request/reopen_merge_request")

    def test_merge(self):
        self.assertResponse("gitlab/merge_request/merge_merge_request")


class NoteTest(ServerTestMixin):

    def test_commit(self):
        self.assertResponse("gitlab/note/commit_note")

    def test_issue(self):
        self.assertResponse("gitlab/note/issue_note")

    def test_merge_request(self):
        self.assertResponse("gitlab/note/merge_request_note")


class PushTest(ServerTestMixin):

    def test_first_commit(self):
        self.assertResponse("gitlab/push/first_commit")

    def test_commit_master_branch(self):
        self.assertResponse("gitlab/push/commit_master_branch")

    def test_create_dev_branch(self):
        self.assertResponse("gitlab/push/create_dev_branch")

    def test_commit_dev_branch(self):
        self.assertResponse("gitlab/push/commit_dev_branch")

    def test_commit_merge_request(self):
        self.assertResponse("gitlab/push/commit_merge_request")

    def test_tag(self):
        self.assertResponse("gitlab/tag_push/tag")


class BuildTest(ServerTestMixin):

    port = get_available_port()
    url = "/new_ci_event?mattermost_webhook_url=http://127.0.0.1:{}".format(port)

    def test_create_build(self):
        self.assertResponse("gitlab/build/create_build_1")

    def test_start_build(self):
        self.assertResponse("gitlab/build/start_build_1")

    def test_failed_build(self):
        self.assertResponse("gitlab/build/failed_build")

    def test_successful_build(self):
        self.assertResponse("gitlab/build/successful_build")


if __name__ == '__main__':
    unittest.main()
