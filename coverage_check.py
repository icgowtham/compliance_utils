"""Utility to detect code coverage and existence of unit test files."""

import argparse
import os
import sys

import config as cfg
import helper_utils as helper
from compliance_check import Compliance


class CoverageCheckCompliance(Compliance):
    """Class to handle the check for coverage."""

    def parse_args(self, description=None):
        """
        Parse command line arguments.

        Overrides from class Compliance, since the options are totally different.

        :param description: str
            Description of the program.
        :return: object
        """
        self._parser = argparse.ArgumentParser()

        self._parser.add_argument("-cov-pm",
                                  "--pre-merge-coverage-check",
                                  nargs=2,
                                  metavar=("source-branch", "target-branch"),
                                  dest="pre_merge_coverage_check",
                                  help="Check coverage for files before merge")

        return self._parser

    def _get_parser(self):
        """
        Getter for 'parser'.

        :return: object
        """
        return self._parser.parse_args()

    def check(self, files_list):
        """
        Check for coverage and unit tests.

        :param files_list: list
            List to files to check.
        :return: None
        """
        CoverageCheckCompliance.check_coverage(files_list)

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

        if args.pre_merge_coverage_check:
            files_list = helper.get_diff_between_branches(
                    args.preMergeCoverageCheck[0],
                    args.preMergeCoverageCheck[1]
            )
        else:
            files_list = helper.get_files_to_be_committed()

        return files_list

    @staticmethod
    def check_coverage(files_list):
        """
        Check the code coverage.

        Check only those files that are part of Eureka infrastructure from the list of files
        to be committed.

        :param files_list: list
            List to files to check.
        :return: None
        """
        change_set = helper.filter_files(files_list)
        file_to_coverage_pct_map = dict()
        # Use a 'set' to reduce the coverage check execution time.
        coverage_dir_set = set()

        for file_name in change_set:
            coverage_dir = os.path.dirname(file_name)
            # Instead of looping through each parent directory of the file, check coverage only once for the parent
            # directory. For e.g., suppose the files to check coverage are 'tmpdir/a.py' and 'tmpdir/b.py', instead of
            # executing the coverage check twice, check only once since the parent directory remains the same.
            coverage_dir_set.add(coverage_dir)

        for coverage_dir in coverage_dir_set:
            print("Checking in %s" % coverage_dir)
            file_to_coverage_pct_map.update(CoverageCheckCompliance.get_coverage(coverage_dir))

        files_missing_coverage = set()

        # Check the files for their coverage.
        for file_name in change_set:
            file_dir_name = os.path.dirname(file_name)
            if file_dir_name.split('/')[-1] in cfg.IGNORE_LIST:
                continue

            if file_name in file_to_coverage_pct_map:
                try:
                    coverage_pct = int(file_to_coverage_pct_map[file_name][:-1])
                except ValueError:
                    print("ERROR: Could not get the correct coverage percentage for {fn}".format(fn=file_name))
                else:
                    if coverage_pct < cfg.CUT_OFF_CODE_COVERAGE_PCT:
                        error_msg = cfg.ERROR_MSG + " WARNING: Coverage for {fn} is at {pct} only!".format(
                                fn=file_name, pct=file_to_coverage_pct_map[file_name])
                        print(error_msg)
                        files_missing_coverage.add(file_name + " -> " + file_to_coverage_pct_map[file_name])
        if files_missing_coverage:
            error_msg = cfg.ERROR_MSG + " The below files are missing expected coverage:\n"
            print("\n" + error_msg + "\n".join(files_missing_coverage))
            sys.exit(1)

    @staticmethod
    def get_coverage(coverage_dir):
        """
        Get coverage for files in the Eureka infra directories.

        :param coverage_dir: str
            The directory to run the coverage report on.
        :return: dict
            A dictionary with file as key and coverage percentage as value.
        """
        # Pass just the 'coverage_dir' directory to 'pytest' so that we do not get collection errors.
        # We are only interested in the coverage report.
        coverage_cmd = ["pytest", "-qs", coverage_dir, "--cov=" + coverage_dir, "--cov-report=term:skip-covered"]
        # Skip those which have 100% coverage already.
        # The 'Coverage.py' gives a warning about no files being collected and on Python 3
        # 'subprocess.check_returncode()' throws an exception. We want the coverage report to get the data from.
        cmd_output_list = helper.execute_shell_command(command=coverage_cmd, is_check_for_exit_code=False)
        # Create a list from those lines which have a '%' (i.e. the coverage)
        coverage_list = [output for output in cmd_output_list if '%' in output]
        # Get the first and last columns (i.e., file name and coverage %) from each list element.
        file_to_coverage_pct_map = dict((item.split()[0], item.split()[-1])
                                        for item in coverage_list)
        return file_to_coverage_pct_map


def main():
    """Main function."""
    compliance = CoverageCheckCompliance()
    files_list = compliance.get_files_list('')
    compliance.check(files_list)


if __name__ == '__main__':
    main()
