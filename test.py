import unittest
import os

from dkmonitor.utilities.dir_scan import dir_scan


DIR_SCAN_DIR = 'test/dir_scan_test'

class TestUtilities(unittest.TestCase):
    """Tests for dir_scan fucntions"""

    def test_dir_scan(self):
        """
        test dir scan
        TODO:
            Test Errors
        """

        #Test basic directory
        test_files = tuple(dir_scan(DIR_SCAN_DIR))
        assert(test_files == (os.path.join(DIR_SCAN_DIR, 'test1.1'),
                              os.path.join(DIR_SCAN_DIR, 'test1.2'),
                              os.path.join(DIR_SCAN_DIR, 'tl2/test2.1'),
                              os.path.join(DIR_SCAN_DIR, 'tl2/test2.2')))

if __name__ == '__main__':
    test_classes = ()
    test_suite = unittest.TestSuite()
    for test_class in test_classes:
        test_suite.addTest(test_class())

    runner = unittest.TextTestRunner()
    runner.run(test_suite)
