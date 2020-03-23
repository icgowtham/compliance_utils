"""Module with various utility functions."""
import ast
import datetime
import importlib
import os
import pytest
import re
import subprocess
import sys

from config import (
    COMPLIANCE_CHECK_PLUGINS_FOLDER,
    GIT_DIFF_FILTER,
)


class NotValidGitRepoException(Exception):
    """The not a valid Git repo exception class."""


def execute_shell_command(command, is_check_for_exit_code=True):
    """
    Execute an external shell command using subprocess module.

    :param command: list
        List containing the command to execute and its arguments.
    :param is_check_for_exit_code: boolean
        Boolean value to indicate whether to check for non-zero exit status (Python 3 only).

    :return: list
        Command output in list form.
    """
    cmd = subprocess.run(command, stdout=subprocess.PIPE)
    if is_check_for_exit_code:
        cmd.check_returncode()
    # Filter out the empty element and '\n' from the output.
    cmd_output = list(filter(None, cmd.stdout.decode('utf-8').split('\n')))
    return cmd_output


def is_inside_git_repo_dir():
    """
    Check whether inside a Git repo directory.

    :param: None
    :return: boolean
    """
    check_cmd = ["git", "rev-parse", "--is-inside-work-tree"]
    cmd_output = execute_shell_command(command=check_cmd)
    cmd_output = ''.join(cmd_output)
    return cmd_output == 'true'


def get_current_branch():
    """
    Get the current Git branch name.

    :param: None
    :return: str
        The current Git branch name.
    """
    if is_inside_git_repo_dir():
        current_branch_cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        current_branch = execute_shell_command(command=current_branch_cmd)
        current_branch = ''.join(current_branch)
        print("Current Git branch is {branch}".format(branch=current_branch))
        return current_branch
    else:
        raise NotValidGitRepoException("Not inside a valid Git repository.")


def get_repo_base_dir():
    """
    Get the base repository path.

    :param: None
    :return: str
        Full path of the Git repository on disk.
    """
    if is_inside_git_repo_dir():
        repo_base_path_cmd = ["git", "rev-parse", "--show-toplevel"]
        repo_base_path = execute_shell_command(command=repo_base_path_cmd)
        repo_base_path = ''.join(repo_base_path)
        print("The Git base repository path is: {path}".format(path=repo_base_path))
        return repo_base_path
    else:
        raise NotValidGitRepoException("Not inside a valid Git repository.")


def get_files_to_be_committed():
    """
    Get the list of files to be committed.

    :param: None
    :return: list
        List of files that are 'add'ed and yet to be 'commit'ted.
    """
    if is_inside_git_repo_dir():
        files_to_commit_cmd = ["git",
                               "diff",
                               "HEAD",
                               "--diff-filter" + "=" + GIT_DIFF_FILTER,
                               "--name-only",
                               "--cached"]
        files_to_commit = execute_shell_command(command=files_to_commit_cmd)
        print("The total number of files to be committed is: {num}".format(num=len(files_to_commit)))
        return files_to_commit
    else:
        raise NotValidGitRepoException("Not inside a valid Git repository.")


def get_diff_between_branches(source_branch=None, target_branch=None):
    """
    Get the list of names of the changed files between branches.

    :param source_branch: str
        Source Git branch name to compare with, defaults to 'dev' branch.
    :param target_branch: str
        Target Git branch name, defaults to current branch.
    :return: list
        List of files differing between the branches.
    """
    if is_inside_git_repo_dir():
        if source_branch is None:
            source_branch = "dev"
        if target_branch is None:
            target_branch = get_current_branch()

        # If both the source and target branches are the same, then do nothing, just return an empty list.
        if source_branch == target_branch:
            print("Both source and target branches are the same. Nothing to do, exiting ...")
            return []

        # Note the 3 dots, since we only want the changes from the target branch.
        # https://stackoverflow.com/a/11163196
        changed_files_cmd = ["git",
                             "diff",
                             source_branch + "..." + target_branch,
                             "--diff-filter" + "=" + GIT_DIFF_FILTER,
                             "--name-only"]
        # Filter out the empty element and '\n' from the output.
        change_list = execute_shell_command(command=changed_files_cmd)
        print("The total number of files changed between branches '{src}' and '{tgt}' is: {num}".format(
                src=source_branch, tgt=target_branch, num=len(change_list)))
        return change_list
    else:
        raise NotValidGitRepoException("Not inside a valid Git repository.")


def get_file_modification_time(filename, is_human_readable=False, dt_format=None):
    """
    Get modification time of a file.

    On Linux based systems, currently there is no way to get the file creation time.
    For more details see: https://stackoverflow.com/a/39501288

    :param filename: str
        Name of the file with either relative or full path.
    :param is_human_readable: boolean
        Boolean flag to return the value in human readable format.
    :param dt_format: str
        Format specifier (time or date) for the output. For e.g., "%m-%d-%Y"
    """
    if os.path.isfile(filename):
        timestamp = os.path.getmtime(filename)
        if is_human_readable:
            return datetime.datetime.fromtimestamp(float(timestamp)).strftime(
                    dt_format if dt_format else "%d/%m/%Y")
        return timestamp
    else:
        print("The file, {file}, no longer exists!".format(file=filename))
        return "01/01/1900"


def run_unit_tests_for_module(module_path):
    """
    Execute unit tests for a given module.

    :param module_path: str
        Relative path (relative to the base Git repo path) of the module
        for which unit tests need to be executed.
    :return: int
        Exit code from 'pytest'.
    """
    print("Executing unit tests for: {mod}".format(mod=module_path))
    exit_code = pytest.main(['-qs', os.path.join(get_repo_base_dir(), module_path)])
    return exit_code


def filter_files(files_list):
    """
    Filter files from the input list.

    :param files_list : files
        The list of files to be filtered
    :return
        The filtered file list
    """
    regexp = re.compile(r".*.py$")
    python_files = [m.group(0) for m in map(regexp.match, files_list) if m is not None]
    return python_files


def parse_file(file_name):
    """
    Parse the given file using 'ast' to further usage.

    :param file_name: str
        The file which has to be parsed.
    :return: str
        Parsed file contents.
    """
    with open(file_name, "r") as file:
        file_contents = ast.parse(file.read(), filename=file_name)
    return file_contents


def get_program_details(file_name,
                        is_imports=False,
                        is_function_defs=False,
                        is_function_calls=False,
                        is_return_types=False):
    """
    Get various parts of a Python program file based on the boolean values.

    :param file_name: str
        The Python program file to get the contents from.
    :param is_imports: boolean
        Set this if import objects are required.
    :param is_function_defs: boolean
        Set this if function definition objects are required.
    :param is_function_calls: boolean
        Set this if function call objects are required.
    :param is_return_types: boolean
        Set this if return objects are required.
    :return: list
    """
    file_contents = parse_file(file_name)
    if is_function_defs:
        function_definitions = [item for item in ast.walk(file_contents) if isinstance(item, ast.FunctionDef)]
        return function_definitions
    if is_imports:
        import_objects = set()
        for node in ast.walk(file_contents):
            if isinstance(node, ast.Import):
                import_objects.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                import_objects.add(node.module)
                for alias in node.names:
                    module_name = '{}.{}'.format(node.module, alias.name)
                    if module_name in sys.modules:
                        import_objects.add(module_name)
        return list(import_objects)
    if is_function_calls:
        call_objects = [item for item in ast.walk(file_contents) if isinstance(item, ast.Call)]
        return call_objects
    if is_return_types:
        return_objects = [item for item in ast.walk(file_contents) if isinstance(item, ast.Return)]
        return return_objects
    return []


def get_function_names_from_file(file_name):
    """
    Get the names of functions from a given file.

    :param file_name:: str
        Name of the file from which to retrieve the function names.
    :return: list
        List containing function names.
    """
    function_definitions = get_program_details(file_name=file_name, is_function_defs=True)
    function_names_list = []
    for func in function_definitions:
        function_names_list.append(func.name)
    return function_names_list


def get_imported_modules_from_file(file_name):
    """
    Get the list of module names which are imported in a given file.

    :param file_name:
        The Python program file from which to get the list of imported module names.
    :return: list
    """
    return get_program_details(file_name=file_name, is_imports=True)


def get_function_calls_from_file(file_name):
    """
    Get the list of function names which are called in a given file.

    :param file_name: str
        The Python program file from which to get the list of function names which are called.
    :return: list
    """
    call_objects = get_program_details(file_name=file_name, is_function_calls=True)
    function_calls = set()
    for calls in call_objects:
        if isinstance(calls.func, ast.Name):
            function_calls.add(calls.func.id)
    return function_calls


def get_function_returns_from_file(file_name):
    """
    Get a dictionary containing function name and its corresponding return type object in a given file.

    NOTE: This does not work as expected. This is still WIP.

    :param file_name:
        The Python program file from which to get the list of function returns.
    :return: dict
    """
    func_name_to_ret_type_obj_map = {}
    function_definitions = get_program_details(file_name=file_name, is_function_defs=True)
    for func_def_obj in function_definitions:
        for func_body in func_def_obj.body:
            if isinstance(func_body, ast.Return):
                func_name_to_ret_type_obj_map[func_def_obj.name] = func_body
    return func_name_to_ret_type_obj_map


def get_plugins(plugin_folder=None):
    """
    Get all the plugins from a folder.

    :param plugin_folder: str
        Path of the folder containing the plugins.
    :return: list
        List of plugins.
    """
    if plugin_folder is None:
        plugin_folder = COMPLIANCE_CHECK_PLUGINS_FOLDER
    plugins_list = []
    plugin_scripts = os.listdir(plugin_folder)
    for script in plugin_scripts:
        if script.startswith("check") and script.endswith(".py"):
            script_path = plugin_folder + os.path.sep + script
            module_name = '.'.join(script_path.split('/'))
            plugin, extn = os.path.splitext(module_name)
            plugins_list.append(plugin)
    return plugins_list


def load_plugin(plugin):
    """
    Load a plugin(module) using 'import_lib'.

    :param plugin: str
        Name of the plugin to load.

    :return: object
        Loaded module object.
    """
    try:
        return importlib.import_module(plugin)
    except ImportError:
        print("Could not load {plugin}, returning ...".format(plugin=plugin))
        return None
