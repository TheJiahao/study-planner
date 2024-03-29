import os
import unittest

from entities.course import Course
from services.import_service import FileCorruptedError, import_service


class TestImportService(unittest.TestCase):
    def setUp(self):
        dirname = os.path.dirname(__file__)

        self.data_directory = os.path.join(dirname, "..", "data")

    def test_read(self):
        file = os.path.join(self.data_directory, "sample.json")

        courses = import_service.read(file)

        self.assertEqual(len(courses), 3)
        self.assertEqual(courses[0], Course("A", 5, {2}, course_id=1))
        self.assertEqual(courses[1], Course("B", 5, {1, 4}, {1}, course_id=2))
        self.assertEqual(courses[2], Course("C", 10, {3}, {1}, course_id=3))

    def test_read_empty_file_raises_error(self):
        file = os.path.join(self.data_directory, "empty.json")

        with self.assertRaises(FileCorruptedError):
            import_service.read(file)

    def test_read_with_corrupted_file_raises_error(self):
        file = os.path.join(self.data_directory, "sample_corrupted.json")

        with self.assertRaises(FileCorruptedError):
            import_service.read(file)

    def test_read_with_typeerror_raises_error(self):
        file = os.path.join(self.data_directory, "sample_typeerror.json")

        with self.assertRaises(FileCorruptedError):
            import_service.read(file)

    def test_read_with_keyerror_raises_error(self):
        file = os.path.join(self.data_directory, "sample_keyerror.json")

        with self.assertRaises(FileCorruptedError):
            import_service.read(file)
