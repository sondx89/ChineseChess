import unittest
import os
from src.utils.log import log_info, log_warning, log_error

class TestLog(unittest.TestCase):
    def setUp(self):
        # Xóa file log trước mỗi test
        if os.path.exists("game.log"):
            os.remove("game.log")

    def test_log_info(self):
        log_info("This is an info message.")
        self.assertTrue(os.path.exists("game.log"))

    def test_log_warning(self):
        log_warning("This is a warning message.")
        self.assertTrue(os.path.exists("game.log"))

    def test_log_error(self):
        log_error("This is an error message.")
        self.assertTrue(os.path.exists("game.log"))

if __name__ == "__main__":
    unittest.main()