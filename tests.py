#!/usr/bin/env python
import unittest
from calculate_fleet_summary import InputValidationError, parse_line,\
        process_file


class LineValidationTests(unittest.TestCase):

    def test_proper(self):
        host_id, instance_type, \
         num_slots, slot_info = parse_line("0,M1,2,0,1", 1)
        self.assertEqual(0, host_id)
        self.assertEqual("M1", instance_type)
        self.assertEqual(2, num_slots)
        self.assertEqual([0, 1], slot_info)

    def test_non_integer_host_id(self):
        self.assertRaises(InputValidationError, parse_line, "foo,M1,2,0,1", 1)

    def test_unknown_instance(self):
        self.assertRaises(InputValidationError, parse_line, "0,2M,2,0,1", 1)

    def test_incorrect_num_slots(self):
        self.assertRaises(InputValidationError, parse_line, "0,M1,2,0,1,0", 1)

    def test_non_integer_num_slots(self):
        self.assertRaises(InputValidationError, parse_line, "0,M1,two,0,1", 1)

    def test_num_slots_zero(self):
        self.assertRaises(InputValidationError, parse_line, "0,M1,0", 1)

    def test_non_integer_slot_info(self):
        self.assertRaises(InputValidationError, parse_line, "0,M1,2,0,one", 1)

    def test_slot_info_not_zero_or_one(self):
        self.assertRaises(InputValidationError, parse_line, "0,M1,2,0,2", 1)


class FileValidationTests(unittest.TestCase):

    def test_proper(self):
        process_file("testdata/valid.txt", "testoutput.txt")

    def test_duplicate_host_id(self):
        self.assertRaises(InputValidationError, process_file,
                          "testdata/duplicate_host_id.txt", "testoutput.txt")

    def test_empty_lines(self):
        self.assertRaises(InputValidationError, process_file,
                          "testdata/empty_lines.txt", "testoutput.txt")

    def test_all_seroes(self):
        process_file("testdata/allzeroes.txt", "testdata/allzeroes.output")

    def test_all_ones(self):
        process_file("testdata/allones.txt", "testdata/allones.output")

    def test_single_instance_type(self):
        process_file("testdata/single_instance_type.txt", "testdata/single_instance_type.output")



if __name__ == "__main__":
    unittest.main(verbosity=2)
