"""Unit tests for helper_utils."""
import pytest
import helper_utils as helper
from mock import patch


@pytest.mark.positive
def test_is_inside_git_repo_dir():
    """
    Unit test for 'is_inside_git_repo_dir'.

    :return: None
    """
    assert (helper.is_inside_git_repo_dir())


@pytest.mark.positive
def test_get_current_branch():
    """
    Unit test for 'get_current_branch'.

    :return: None
    """
    cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    cmd_output = helper.execute_shell_command(command=cmd)
    branch = ''.join(cmd_output)
    assert (branch == helper.get_current_branch())


@pytest.mark.positive
def test_get_repo_base_dir():
    """
    Unit test for 'get_repo_base_dir'.

    :return: None
    """
    cmd = ["git", "rev-parse", "--show-toplevel"]
    cmd_output = helper.execute_shell_command(command=cmd)
    path = ''.join(cmd_output)
    assert (path == helper.get_repo_base_dir())


@pytest.mark.positive
@patch('helper_utils.get_files_to_be_committed')
def test_get_files_to_be_committed(mock_get_files_to_be_committed):
    """
    Unit test for 'get_files_to_be_committed'.

    :param mock_get_files_to_be_committed: MANDATORY mock object @n
    :return: None
    """
    mock_get_files_to_be_committed.return_value = ["eureka/connections/ssh/ssh.py",
                                                   "framework/executor/api.py",
                                                   "testApi/heuristics.py"]
    assert (len(helper.get_files_to_be_committed()) > 0)


@pytest.mark.positive
@patch('helper_utils.get_diff_between_branches')
def test_get_diff_between_branches(mock_get_diff_between_branches):
    """
    Unit test for 'get_diff_between_branches'.

    :param mock_get_diff_between_branches: MANDATORY mock object @n
    :return: None
    """
    files_list = helper.get_diff_between_branches(source_branch='dev', target_branch='dev')
    assert (len(files_list) == 0)
    mock_get_diff_between_branches.return_value = ["eureka/connections/ssh/ssh.py",
                                                   "framework/executor/api.py",
                                                   "testApi/heuristics.py"]
    files_list = helper.get_diff_between_branches()
    assert (len(files_list) > 0)


@pytest.mark.positive
def test_get_file_modification_time():
    """
    Unit test for 'get_file_modification_time'.

    :return: None
    """
    # Testing with some non-existent file
    assert (helper.get_file_modification_time(filename="zzz.py",
                                              is_human_readable=True) == "01/01/1900")


@pytest.mark.positive
def test_filter_files():
    """
    Unit test for 'filter_files'.

    :return: None
    """
    files_list = ["compliance_check.py",
                  "coverage_check.py",
                  "config.py"]
    assert (len(helper.filter_files(files_list=files_list)) == 3)


@pytest.mark.positive
def test_get_program_details():
    """
    Unit test for 'get_program_details'.

    :return: None
    """
    assert (len(helper.get_program_details(file_name=__file__)) == 0)


@pytest.mark.positive
def test_get_function_names_from_file():
    """
    Unit test for 'get_function_names_from_file'.

    :return: None
    """
    assert (len(helper.get_function_names_from_file(file_name=__file__)) > 0)


@pytest.mark.positive
def test_get_imported_modules_from_file():
    """
    Unit test for 'get_imported_modules_from_file'.

    :return: None
    """
    assert (len(helper.get_imported_modules_from_file(file_name=__file__)) > 0)


@pytest.mark.positive
def test_get_function_calls_from_file():
    """
    Unit test for 'get_function_calls_from_file'.

    :return: None
    """
    assert (len(helper.get_function_calls_from_file(file_name=__file__)) > 0)
