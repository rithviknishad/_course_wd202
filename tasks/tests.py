from django.test import TestCase


class QuestionModelTests(TestCase):
    def test_always_fail(self):
        """
        This test will always fail ( for now )
        """
        self.assertIs(True, False)
