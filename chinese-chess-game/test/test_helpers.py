import unittest
from src.utils.helpers import position_to_coordinates, coordinates_to_position

class TestHelpers(unittest.TestCase):
    def test_position_to_coordinates(self):
        self.assertEqual(position_to_coordinates("A1"), (0, 0))
        self.assertEqual(position_to_coordinates("C3"), (2, 2))
        self.assertEqual(position_to_coordinates("H9"), (8, 7))

    def test_coordinates_to_position(self):
        self.assertEqual(coordinates_to_position(0, 0), "A1")
        self.assertEqual(coordinates_to_position(2, 2), "C3")
        self.assertEqual(coordinates_to_position(8, 7), "H9")

if __name__ == "__main__":
    unittest.main()