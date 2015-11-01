#!/usr/bin/env python
import filecmp
import unittest
import os
import re
from calculate_fleet_summary import InputValidationError, parse_line,\
        process_file, INSTANCE_TYPES

# In the regex definitions below it is assumed that instance_type names will
# consist of a mixture of alphabetical and numeric characters. This is only
# a quick check, because the actual instance type value is checked outside the
# scope of the regexes.

# Regex matching "<instance_type>=<count>;".
INSTANCE_COUNT_RE = re.compile(r"([a-zA-Z0-9]+)=([0-9]+);")

# Regex matching "M2=<count>,<empty slots>;"
INSTANCE_COUNT_SLOTS_RE = re.compile(r"([a-zA-Z0-9]+)=([0-9]+),([0-9]+);")


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

    def test_unknown_instance_type(self):
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

    def test_duplicate_host_id(self):
        self.assertRaises(InputValidationError, process_file,
                          "testdata/duplicate_host_id.txt",
                          "shouldnotbegenerated.txt")

    def test_empty_lines(self):
        self.assertRaises(InputValidationError, process_file,
                          "testdata/empty_lines.txt",
                          "shouldnotbegenerated.txt")

    # TODO: The functions below can be refactored.

    def test_proper(self):
        output_file = "testdata/valid.output"
        self.assertTrue(process_file("testdata/valid.txt",
                                     output_file))
        self.validate_output(output_file)
        self.assertTrue(filecmp.cmp(output_file, "testdata/valid.expected"))
        os.remove(output_file)

    def test_all_zeroes(self):
        output_file = "testdata/allzeroes.output"
        self.assertTrue(process_file("testdata/allzeroes.txt",
                                     output_file))
        self.validate_output(output_file)
        self.assertTrue(filecmp.cmp(output_file, "testdata/allzeroes.expected"))
        os.remove(output_file)

    def test_all_ones(self):
        output_file = "testdata/allones.output"
        self.assertTrue(process_file("testdata/allones.txt",
                                     output_file))
        self.validate_output(output_file)
        self.assertTrue(filecmp.cmp(output_file, "testdata/allones.expected"))
        os.remove(output_file)

    def test_single_instance_type(self):
        output_file = "testdata/single_instance_type.output"
        self.assertTrue(process_file("testdata/single_instance_type.txt",
                                     output_file))
        self.validate_output(output_file)
        self.assertTrue(filecmp.cmp(output_file, "testdata/single_instance_type.expected"))
        os.remove(output_file)

    def validate_output(self, file_name):
        """Structural integrity check on generated output.

        :param str file_name:
        """
        with open(file_name, "r") as f:
            line = f.readline()
            # Expected: "EMPTY: <instance_type>=<count>; ..."
            parts = line.split()
            self.assertEqual("EMPTY:", parts[0])
            num_instance_types = len(INSTANCE_TYPES)
            self.assertEqual(num_instance_types, len(parts) - 1)
            for i in xrange(0, num_instance_types):
                m = re.match(INSTANCE_COUNT_RE, parts[i + 1])
                self.assertIsNotNone(m)
                self.assertEqual(INSTANCE_TYPES[i], m.group(1))
                # m.group(2) is the integer value.
                # The regex match is sufficient validation.

            line = f.readline()
            # Expected: "FULL: <instance_type>=<count>; ..."
            parts = line.split()
            self.assertEqual("FULL:", parts[0])
            num_instance_types = len(INSTANCE_TYPES)
            self.assertEqual(num_instance_types, len(parts) - 1)
            for i in xrange(0, num_instance_types):
                m = re.match(INSTANCE_COUNT_RE, parts[i + 1])
                self.assertIsNotNone(m)
                self.assertEqual(INSTANCE_TYPES[i], m.group(1))
                # m.group(2) is the integer value.
                # The regex match is sufficient validation.

            line = f.readline()
            # Expected:
            # "MOST FILLED: <instance_type>=<count>,<empty slots>; ..."
            parts = line.split()
            self.assertEqual("MOST", parts[0])
            self.assertEqual("FILLED:", parts[1])
            num_instance_types = len(INSTANCE_TYPES)
            self.assertEqual(num_instance_types, len(parts) - 2)
            for i in xrange(0, num_instance_types):
                m = re.match(INSTANCE_COUNT_SLOTS_RE, parts[i + 2])
                self.assertIsNotNone(m)
                self.assertEqual(INSTANCE_TYPES[i], m.group(1))
                # m.group(2) and m.group(3) are the integer values.
                # The regex match is sufficient validation.

            # Verify that we have reached the end of the file
            line = f.readline()
            self.assertEqual("", line)


if __name__ == "__main__":
    unittest.main(verbosity=2)
