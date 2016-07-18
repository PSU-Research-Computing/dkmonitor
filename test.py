import unittest
import os
import logging

from dkmonitor.utilities.dir_scan import dir_scan
from dkmonitor.utilities.log_setup import setup_logger


SCAN_DIR = 'test/dir_scan_test'
LOG_FILE_NAME = 'test/test_log_file.log'

class TestUtilities(unittest.TestCase):
    """
    Tests for dir_scan fucntions
    TODO:
        Test Errors
    """

    def test_dir_scan(self):
        """
        test dir scan
        """

        #Test basic directory
        test_files = tuple(dir_scan(SCAN_DIR))
        self.assertEqual(test_files, (os.path.join(SCAN_DIR, 'test1.1'),
                                      os.path.join(SCAN_DIR, 'test1.2'),
                                      os.path.join(SCAN_DIR, 'tl2/test2.1'),
                                      os.path.join(SCAN_DIR, 'tl2/test2.2')))

    def test_setup_logger(self):
        """Test logging setup function"""
        assert(isinstance(setup_logger(LOG_FILE_NAME), logging.Logger))


if __name__ == '__main__':
    test_classes = ()
    test_suite = unittest.TestSuite()
    for test_class in test_classes:
        test_suite.addTest(test_class())

    runner = unittest.TextTestRunner()
    runner.run(test_suite)
