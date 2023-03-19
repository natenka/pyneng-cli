import sys
import re
import os
import json
from glob import glob

import click
import pytest
from rich.console import Console
from rich.markdown import Markdown
from pytest_jsonreport.plugin import JSONReport

from pyneng_cli import (
    DEFAULT_BRANCH,
    TASK_DIRS,
    DB_TASK_DIRS,
    TASK_NUMBER_DIR_MAP,
)
from pyneng_cli.exceptions import PynengError
from pyneng_cli.pyneng_docs import DOCS
from pyneng_cli.utils import (
    red,
    green,
    save_changes_to_github,
    current_chapter_id,
    current_dir_name,
    parse_json_report,
    copy_answers,
    update_tasks_and_tests,
    update_chapters_tasks_and_tests,
)


def exception_handler(exception_type, exception, traceback):
    """
    sys.excepthook to disable traceback by default
    """
    print(f"\n{exception_type.__name__}: {exception}\n")


def check_current_dir_name(dir_list, message):
    current_chapter = current_dir_name()
    if current_chapter not in dir_list:
        task_dirs_line = "\n    ".join(
            [d for d in dir_list if not d.startswith("task")]
        )
        print(red(f"\n{message}:" f"\n    {task_dirs_line}"))
        raise click.Abort()


def _get_tasks_tests_from_cli(self, value):
    regex = (
        r"(?P<all>all)|"
        r"(?P<number_star>\d\*)|"
        r"(?P<letters_range>\d[a-i]-[a-i])|"
        r"(?P<numbers_range>\d-\d)|"
        r"(?P<single_task>\d[a-i]?)"
    )
    tasks_list = re.split(r"[ ,]+", value)
    current_chapter = current_chapter_id()
    test_files = []
    task_files = []
    for task in tasks_list:
        match = re.fullmatch(regex, task)
        if match:
            if task == "all":
                test_files = sorted(glob(f"test_task_{current_chapter}_*.py"))
                task_files = sorted(glob(f"task_{current_chapter}_*.py"))
                break
            else:
                if match.group("letters_range"):
                    task = f"{task[0]}[{task[1:]}]"  # convert 1a-c to 1[a-c]
                elif match.group("numbers_range"):
                    task = f"[{task}]"  # convert 1-3 to [1-3]

                test_files += glob(f"test_task_{current_chapter}_{task}.py")
                task_files += glob(f"task_{current_chapter}_{task}.py")
        else:
            self.fail(
                red(
                    f"This format is not supported {task}. "
                    "Acceptable formats are listed in pyneng --help"
                )
            )
    tasks_with_tests = set([test.replace("test_", "") for test in test_files])
    tasks_without_tests = set(task_files) - tasks_with_tests
    return sorted(test_files), sorted(tasks_without_tests), sorted(task_files)


class CustomTasksType(click.ParamType):
    """
    The class creates a new type for click and converts valid task string
    options into separate test files.

    In addition, it checks whether there is such a file in the current
    directory and leaves only those that are.
    """

    name = "CustomTasksType"

    def convert(self, value, param, ctx):
        if isinstance(value, tuple):
            return value
        elif value == "all" and current_dir_name() == "exercises":
            return value
        elif current_dir_name() not in TASK_DIRS:
            return value

        return _get_tasks_tests_from_cli(self, value)


class CustomChapterType(click.ParamType):
    name = "Chapters"

    def convert(self, value, param, ctx):
        if isinstance(value, tuple):
            return value
        regex = r"(?P<numbers_range>\d+-\d+)|" r"(?P<number>\d+)"
        TASK_NUMBER_DIR_MAP
        chapter_dir_list = []
        chapter_list = re.split(r"[ ,]+", value)
        for chapter in chapter_list:
            match = re.fullmatch(regex, chapter)
            if match:
                if match.group("number"):
                    chapter = int(match.group("number"))
                    chapter_dir = TASK_NUMBER_DIR_MAP.get(chapter)
                    if chapter_dir:
                        chapter_dir_list.append(chapter_dir)
                elif match.group("numbers_range"):
                    start, stop = match.group("numbers_range").split("-")
                    for chapter_id in range(int(start), int(stop) + 1):
                        chapter_dir = TASK_NUMBER_DIR_MAP.get(chapter_id)
                        if chapter_dir:
                            chapter_dir_list.append(chapter_dir)
            else:
                self.fail(
                    red(
                        f"This format is not supported {chapter}. "
                        "Valid formats in pyneng --help"
                    )
                )
        return sorted(chapter_dir_list)


def print_docs_with_pager(width=90):
    console = Console(width=width)
    md = Markdown(DOCS)
    with console.pager():
        console.print(md)


@click.command(
    context_settings=dict(
        ignore_unknown_options=True, help_option_names=["-h", "--help"]
    )
)
@click.argument("tasks", default="all", type=CustomTasksType())
@click.option(
    "--answer",
    "-a",
    is_flag=True,
    help=(
        "Copy answers for tasks that passed the tests. When this flag is added,"
        "no traceback is output for tests."
    ),
)
@click.option("--docs", is_flag=True, help="Show pyneng documentation")
@click.option(
    "--save-all",
    "save_all_to_github",
    is_flag=True,
    help="Save to GitHub all modified files in the current directory",
)
@click.option(
    "--update", "update_tasks_tests", is_flag=True, help="Update tasks and tests"
)
@click.option(
    "--test-only", "update_tests_only", is_flag=True, help="Update tests only"
)
@click.option(
    "--update-chapters",
    type=CustomChapterType(),
    help="Update all tasks and tests in the specified chapters",
)
@click.option("--disable-verbose", "-d", is_flag=True, help="Disable verbose output")
@click.option("--debug", is_flag=True, help="Show exception traceback")
@click.option("--default-branch", "-b", default="main")
@click.option(
    "--all",
    "git_add_all_to_github",
    is_flag=True,
    help="Add git add .",
)
@click.option("--ignore-ssl-cert", default=False)
@click.version_option(version="4.3.0")
def cli(
    tasks,
    disable_verbose,
    answer,
    debug,
    default_branch,
    git_add_all_to_github,
    ignore_ssl_cert,
    update_tasks_tests,
    update_tests_only,
    save_all_to_github,
    update_chapters,
    docs,
):
    """
    PYNENG-CLI: Run tests for TASKS tasks. By default, all tests will run.

    \b
    These options do not run tests
     pyneng --docs                 Show pyneng documentation
     pyneng --save-all             Save to GitHub all modified files in the current directory
     pyneng --update               Update all tasks and tests in the current directory
     pyneng --update --test-only   Update only tests in the current directory
     pyneng 1,2 --update           Update tasks 1 and 2 and corresponding tests in current directory
     pyneng --update-chapters 4-5  Update chapters 4 and 5 (directories will be removed and updated versions copied)

    \b
    Run tests, view answers
    \b
         pyneng             run all tests for current chapter
         pyneng 1,2a,5      run tests for tasks 1, 2a and 5
         pyneng 1,2*        run tests for tasks 1, all tasks 2 with and without letters
         pyneng 1,3-5       run tests for tasks 1, 3, 4, 5
         pyneng 1-5 -a      run the tests and write the answers for the tasks
                            that passed the tests to the files answer_task_x.py

    \b
    Read more in the documentation: pyneng --docs
    """
    global DEFAULT_BRANCH
    if default_branch != "main":
        DEFAULT_BRANCH = default_branch

    if docs:
        print_docs_with_pager()
        return

    if save_all_to_github:
        save_changes_to_github(branch=DEFAULT_BRANCH)
        print(green("All changes in the current directory are saved to GitHub"))
        return

    if update_chapters:
        LANG = click.prompt(
            "Please select a language from the following",
            type=click.Choice(["uk", "en", "ru"]),
        )
        check_current_dir_name(
            ["exercises"], "Chapters must be updated from the directory"
        )
        update_chapters_tasks_and_tests(
            update_chapters, branch=DEFAULT_BRANCH, lang=LANG
        )
        return

    # it makes sense to perform further actions only if we are in the directory
    # of a specific task chapter
    check_current_dir_name(
        TASK_DIRS + DB_TASK_DIRS, "Tasks can only be tested from directories"
    )

    test_files, tasks_without_tests, task_files = tasks

    if update_tasks_tests:
        LANG = click.prompt(
            "Please select a language from the following",
            type=click.Choice(["uk", "en", "ru"]),
        )
        if update_tests_only:
            tasks_files = None
            msg = green("Tests updated successfully")
        else:
            msg = green("Tasks and tests updated successfully")

        upd = update_tasks_and_tests(
            task_files, test_files, branch=DEFAULT_BRANCH, lang=LANG
        )
        if upd:
            print(msg)
        return

    if not debug:
        sys.excepthook = exception_handler

    json_plugin = JSONReport()
    pytest_args_common = ["--json-report-file=none", "--disable-warnings"]

    if disable_verbose:
        pytest_args = [*pytest_args_common, "--tb=short"]
    else:
        pytest_args = [*pytest_args_common, "-vv"]

    # if the -a flag is added, it makes no sense to print traceback, since most
    # likely the tasks have already been checked by previous runs.
    if answer:
        pytest_args = [*pytest_args_common, "--tb=no"]

    # run pytest
    pytest.main(test_files + pytest_args, plugins=[json_plugin])

    # get pytest results in JSON format passed_tasks are tasks that have tests
    # and passed tests
    passed_tasks = parse_json_report(json_plugin.report)

    if passed_tasks or tasks_without_tests:
        # copy answers to answer_task_x.py files
        if answer:
            copy_answers(passed_tasks)

    # if the --all flag is added, all changes must be saved to github
    if git_add_all_to_github:
        save_changes_to_github(branch=DEFAULT_BRANCH)


if __name__ == "__main__":
    cli()
