#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""

__author__ = "Sarah Beverton, used logging config from Daniel's example"

import sys
import signal
import time
import argparse
import logging
import os

exit_flag = False

magic_string_lines = {}
logged_files = []

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(name)-12s \
            %(levelname)-8s [%(threadName)-12s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout,
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def scan_single_file(filename, magic_string, dir_path):
    """Searches given filename for magic string and
        returns the line number where the magic string was found"""
    global magic_string_lines
    global logged_files
    full_path = f'{dir_path}/{filename}'
    try:
        with open(full_path, 'r') as f:
            text_list = f.readlines()
            for i, line in enumerate(text_list, 1):
                if magic_string in line and i > magic_string_lines[filename]:
                    logger.info(f'Magic string: \'{magic_string}\' found on line {i} in \
                                        file: {filename}.')
                if i > magic_string_lines[filename]:
                    magic_string_lines[filename] = i
    except OSError:
        logger.info(f'{filename} not found')


def detect_added_files(dir_path, extension):
    """Looks through files in directory and adds them
        if they are not already in dictionary (and they
        have the correct extension) - reports added"""
    global magic_string_lines
    global logged_files

    abs_path = os.path.abspath(dir_path)
    dir_files = os.listdir(abs_path)
    for search_file in dir_files:
        if search_file not in logged_files and search_file.endswith(extension):
            logged_files.append(search_file)
            magic_string_lines[search_file] = 0
            logger.info(f'New file: {search_file} added to dictionary')


def detect_removed_files(dir_path):
    """Looks through files in dictionary to see if they
        still exist in the directory - if not, remove them
        and report as deleted"""
    global magic_string_lines
    global logged_files

    abs_path = os.path.abspath(dir_path)
    dir_files = os.listdir(abs_path)
    for search_file in logged_files:
        if search_file not in dir_files:
            logged_files.remove(search_file)
            del magic_string_lines[search_file]
            logger.info(f'File: {search_file} is no longer in directory \
                        and has been removed from dictionary')


def watch_directory(dir_path, magic_string, extension):
    """Watches given directory for new files or additions to
        files, and searches the files for a magic string"""
    global magic_string_lines

    try:
        abs_path = os.path.abspath(dir_path)
        dir_files = os.listdir(abs_path)
    except OSError:
        logger.info(f'{dir_path} does not exist')
    else:
        detect_added_files(dir_path, extension)
        detect_removed_files(dir_path)
        for search_file in dir_files:
            if search_file.endswith(extension):
                scan_single_file(search_file, magic_string, abs_path)


def signal_handler(sig_num, frame):
    """This is a handler for SIGTERM and SIGINT.
    Main() will exit if SIGINT or SIGTERM are trapped."""
    global exit_flag
    logger.warning('Received signal: ' + signal.Signals(sig_num).name +
                   ', Goodbye!')
    if signal.Signals(sig_num).name == 'SIGINT' or 'SIGTERM':
        exit_flag = True


def create_parser():
    """Creates an argument parser object."""
    parser = argparse.ArgumentParser()
    parser.add_argument('dir_path', help='directory to search')
    parser.add_argument('magic_string', help='text to search for in file')
    parser.add_argument('-e', '--extension', default='.txt',
                        help='file extension to search')
    parser.add_argument('-i', '--interval', default=2, help='polling interval')

    return parser


def main(args):
    start_time = time.time()
    parser = create_parser()

    parsed_args = parser.parse_args(args)

    magic_string = parsed_args.magic_string
    polling_interval = parsed_args.interval
    extension = parsed_args.extension
    dir_path = parsed_args.dir_path

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info(
        '\n' + '-'*80 +
        f'\n\tWatching {dir_path} for files with {extension}' +
        f'\n\tcontaining {magic_string}\n' +
        '-'*80
    )

    while not exit_flag:
        try:
            watch_directory(dir_path, magic_string, extension)
        except Exception as e:
            logger.error(f'Unhandled exception: + {e}')
        time.sleep(int(polling_interval))

    uptime = time.time() - start_time
    logger.info(
        '\n' + '-'*80 +
        f'\n\tStopped {__file__}' +
        f'\n\tUptime was {uptime}\n' +
        '-'*80
    )


if __name__ == '__main__':
    main(sys.argv[1:])
