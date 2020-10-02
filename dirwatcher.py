#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""

__author__ = "Sarah Beverton"

import sys
import signal
import time
import argparse
import re

exit_flag = False


def search_for_magic(filename, magic_string):
    with open(filename, 'r') as f:
        text = f.read()
        text_list = text.split('\n')
        pattern = re.compile(rf"{magic_string}")
        # or maybe re.escape(magic_string) or maybe just re.compile(magic_string)?
        line_nums = []
        for i, line in enumerate(text_list, 1):
            if pattern.search(line):
                line_nums.append(i)
    return line_nums


def watch_directory(path, magic_string, extension, interval):
    # Your code here
    return


def create_parser():
    """Creates an argument parser object."""
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', help='file to search')
    # parser.add_argument('start_line', help='?')
    parser.add_argument('magic_string', help='text to search for in file')
    # parser.add_argument('path', help='directory to search')
    # parser.add_argument('extension', help='what file extension to search')
    # parser.add_argument('interval', help='polling interval')

    return parser


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name
    logger.warn('Received ' + signal.Signals(sig_num).name)


def main(args):
    parser = create_parser()

    if not args:
        parser.print_usage()
        sys.exit(1)

    parsed_args = parser.parse_args(args)

    file_to_search = parsed_args.filename
    magic_string = parsed_args.magic_string
    magic_lines = search_for_magic(file_to_search, magic_string)
    print(f"Magic string found in file {file_to_search} at lines:", magic_lines)

    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.
    """
    while not exit_flag:
        try:
            # call my directory watching function
            pass
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            pass

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(polling_interval)
    """
    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start


if __name__ == '__main__':
    main(sys.argv[1:])
