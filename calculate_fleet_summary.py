#!/usr/bin/env python
"""
Utility for calculating summary statistics for a fleet of hosts.

Each host has a fixed number of slots in which virtual instances can run.
Each host can only run instances of a particular type, e.g. M1, M2, or M3.

The fleet state is read from a file called "FleetState.txt".
Each line in the file represents a single host in the following
comma-separated format:

<HostID>,<InstanceType>,<N>,<Slot1State>,<Slot2State>,...,<SlotNState>
where
<HostID> is an integer
<InstanceType> can be M1, M2, or M3
<N> is the total number of slots on the machine
<SlotjState> is 0 if slot j is empty and 1 if it is occupied by an instance

When invalid input is encountered, the application will terminate immediately
with an informative error message. It does not make sense to continue
computing the statistics on an "incomplete" data set. It is, however, trivial
to change the application to simply ignore erroneous lines.
"""
import collections
import string
import sys

# Note that the order of this list is important as it affects the order
# in which the output statistics are printed.
INSTANCE_TYPES = ["M1", "M2", "M3"]

INPUT_FILENAME = "FleetState.txt"
OUTPUT_FILENAME = "Statistics.txt"


class InputValidationError(Exception):

    def __init__(self, line_number, message):
        self.line_number = line_number
        self.message = message

    def __str__(self):
        return "Line {}: {}".format(self.line_number, self.message)


def parse_line(content, line_number):
    """Parse and validate input lines.

    Assumptions:
    * We assume that a host has at least one slot

    :param str content: The input line
    :param int line_number: The line number in the file (starting at 1)
    :return tuple: (host_id, instance_type, num_slots, slot_info) where
        slot_info is a list of integers
    :raises InputValidation: on
    """

    host_id, instance_type, num_slots, slot_info_list = content.split(',', 3)

    try:
        host_id = int(host_id)
    except ValueError:
        msg = "The host id '{}' is not an integer.".format(host_id)
        raise InputValidationError(line_number, msg)

    if instance_type not in INSTANCE_TYPES:
        msg = "Unknown instance type '{}'".format(instance_type)
        raise InputValidationError(line_number, msg)

    try:
        num_slots = int(num_slots)
    except ValueError:
        msg = "The number of slots '{}' is not an integer.".format(num_slots)
        raise InputValidationError(line_number, msg)

    slot_info = slot_info_list.split(',')

    slot_info_length = len(slot_info)
    if slot_info_length != num_slots:
        msg = "The number of slot information entries ({}) does not match "\
              "the number of slots specified ({}).".format(slot_info_length,
                                                           num_slots)
        raise InputValidationError(line_number, msg)

    try:
        slot_info = map(int, slot_info)
        if not all((x in [0, 1] for x in slot_info)):
            msg = "One or more slot information fields are not 0 or 1."
            raise InputValidationError(line_number, msg)
    except ValueError:
        msg = "One or more slot information fields are not an integers."
        raise InputValidationError(line_number, msg)

    return (host_id, instance_type, num_slots, slot_info)


def get_most_filled_info(instance_type_counters):
    """Find the information relating to the most filled host.

    The exact definition of "most filled" is the "smallest number
    of empty slots > 0".

    :param dict instance_type_counters: {empty_slots: host_count, ...}
    :retuns tuple: (host_count, empty_slots)
    """
    # Find the minimum empty slot count
    empty_slots = min(x for x in instance_type_counters.keys() if x > 0)
    # Get the associated host count
    host_count = instance_type_counters[empty_slots]
    return (host_count, empty_slots)


def process_file(input_filename=INPUT_FILENAME,
                 output_filename=OUTPUT_FILENAME):
    # Initialise counters for the instance types.
    empty_hosts_count = {instance_type: 0 for instance_type in INSTANCE_TYPES}
    full_hosts_count = {instance_type: 0 for instance_type in INSTANCE_TYPES}
    # To be able to find the most filled host counts, we store a dictionary
    # per instance type which will contain keys referring to the number of
    # empty slots and values which are the count of hosts. Using a defaultdict
    # simplifies the code below. See
    # https://docs.python.org/2/library/collections.html#collections.defaultdict
    #
    # {"instance_type": {empty_slots: host_count, ...}, ...}, e.g.
    # {"M1": {2: 5, 7: 4}}
    #
    empty_slots_count = {instance_type: collections.defaultdict(int)
                         for instance_type in INSTANCE_TYPES}
    # Keep track of host_ids seen so far. The same hosts may not appear more
    # than once in the input. Use a set for O(1) lookups.
    host_ids_seen = set()

    with open(input_filename, "r") as input_file:
        line_number = 1
        for line in input_file:
            host_id, instance_type,\
            num_slots, slot_info = parse_line(line, line_number)

            if host_id in host_ids_seen:
                msg = "Host ID '{}' specified more than once.".format(host_id)
                raise InputValidationError(line_number, msg)
            else:
                host_ids_seen.add(host_id)

            if all(x == 0 for x in slot_info):
                empty_hosts_count[instance_type] += 1

            if all(x == 1 for x in slot_info):
                full_hosts_count[instance_type] += 1

            num_filled_slots = sum(slot_info)
            num_empty_slots = num_slots - num_filled_slots

            # defaultdict will initialise new keys to 0
            empty_slots_count[instance_type][num_empty_slots] += 1

            line_number += 1

    with open(output_filename, "w") as output_file:
        stats = string.join([" {}={};".format(instance_type,
                                              empty_hosts_count[instance_type])
                             for instance_type in INSTANCE_TYPES])
        output_file.write("EMPTY:{}\n".format(stats))

        stats = string.join([" {}={};".format(instance_type,
                                              full_hosts_count[instance_type])
                             for instance_type in INSTANCE_TYPES])
        output_file.write("FULL:{}\n".format(stats))

        stats = ""
        for instance_type in INSTANCE_TYPES:
            instance_info = empty_slots_count[instance_type]
            host_count, empty_slots = get_most_filled_info(instance_info)
            stats += " {}={},{};".format(instance_type, host_count,
                                         empty_slots)

        output_file.write("MOST_FILLED:{}\n".format(stats))


if __name__ == "__main__":
    try:
        process_file()
    except Exception, e:
        sys.exit(str(e))
