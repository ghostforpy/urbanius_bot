from django.test import TestCase
from sheduler import tasks

class ShedulerTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")
        pass

    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")
        pass

    def test_send_rating_reminder(self):
        tasks.send_rating_reminder(None)
        self.assertFalse(False)

