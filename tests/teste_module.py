import unittest

import stactools.ga_dlcd


class TestModule(unittest.TestCase):
    def test_version(self):
        self.assertIsNotNone(stactools.ga_dlcd.__version__)