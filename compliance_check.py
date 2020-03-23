"""Abstract class for all compliance checking operations."""
import argparse
from abc import ABCMeta, abstractmethod
from six import add_metaclass
from helper_utils import (get_files_to_be_committed, get_diff_between_branches)


@add_metaclass(ABCMeta)
class Compliance(object):
    """Abstract class for all compliance checking operations."""

    def __init__(self):
    	self._parser = None

    @abstractmethod
    def parse_args(self, description=None):
        """
        Parse the command line arguments.

        :param description: str
            Description of the program.
        :return: object
        """
        self._parser = argparse.ArgumentParser(description=description)
        self._parser.add_argument("-pre-commit",
                                  "--pre-commit-compliance-check",
                                  dest="pre_commit_check",
                                  help="Run compliance on all the files to be committed",
                                  action="store_true")
        self._parser.add_argument("-pre-merge",
                                  "--pre-merge-compliance-check",
                                  nargs=2,
                                  metavar=("source-branch", "target-branch"),
                                  dest="pre_merge_check",
                                  help="Run compliance on all files to be merged.")
        self._parser.add_argument("-path",
                                  "--file-path",
                                  nargs=1,
                                  metavar="file-path",
                                  dest="path",
                                  help="Run compliance on the file(s)/path.")

        return self._parser

    @abstractmethod
    def get_files_list(self, description=None):
        """
        Get the list of files to check.

        :param description: str
            Description of the program.
        :return: list
        """
        files_list = []
        args_parser = self.parse_args(description=description)
        args = args_parser.parse_args()

        if args.pre_commit_check:
            files_list = get_files_to_be_committed()
        elif args.pre_merge_check:
            files_list = get_diff_between_branches(
                    args.pre_merge_check[0],
                    args.pre_merge_check[1]
            )
        elif args.path:
            files_list = args.path

        return files_list

    @abstractmethod
    def check(self, files_list):
        """
        Perform the compliance check.

        :param files_list: list
            List of files to check for compliance
        :return: None
        """
        raise NotImplementedError("Please implement this method as per your requirements.")


class ComplianceViolationException(Exception):
    """The generic compliance violation exception class."""
