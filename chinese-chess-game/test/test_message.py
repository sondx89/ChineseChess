import unittest
from src.utils.message import MESSAGES

class TestMessage(unittest.TestCase):
    def test_messages(self):
        self.assertIn("welcome", MESSAGES)
        self.assertEqual(MESSAGES["welcome"], "Chào mừng bạn đến với trò chơi Cờ Tướng!")
        self.assertIn("invalid_move", MESSAGES)
        self.assertEqual(MESSAGES["invalid_move"], "Nước đi không hợp lệ. Vui lòng thử lại.")

if __name__ == "__main__":
    unittest.main()