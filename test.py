import unittest

target = __import__('main')
check_api_response = target.check_api_response

class TestSum(unittest.TestCase):
    
    # Tests for check api response function:
    def test_successful_response_200(self):
        self.assertTrue(check_api_response(200, "https://example.com"))

    def test_successful_response_201(self):
        self.assertTrue(check_api_response(201, "https://example.com"))

    def test_successful_response_204(self):
        self.assertTrue(check_api_response(204, "https://example.com"))

    def test_unsuccessful_response(self):
        with self.assertRaises(ValueError):
            check_api_response(404, "https://example.com")


if __name__ == '__main__':
    unittest.main()