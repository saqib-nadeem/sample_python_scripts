import os
import json

import unittest

from web_api import app

class FlaskAPPTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_kit_type(self):
        tester = app.test_client(self)
        response = tester.get('/api/v0/kit_type')
        self.assertEqual(response.status_code, 404)

    def test_is_admin(self):
        tester = app.test_client(self)
        response = tester.get('/api/v0/admin/1', content_type='application/json')
        data = json.loads(response.data)
        expected_response = True
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], expected_response)

    def test_page_not_found(self):
        tester = app.test_client(self)
        response = tester.get('/fake-route')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()