import subprocess
from platform import system as system_name
import re
import os
from collections import defaultdict
import tempfile
import pathlib
import stat
import shutil
from datetime import datetime, timedelta

import click
import github
from rich import print as rprint
from rich.padding import Padding

from pyneng_cli.exceptions import PynengError
from pyneng_cli import (
    ANSWERS_URL,
    TASK_DIRS,
    DB_TASK_DIRS,
    TASKS_URL,
    TASKS_LOCAL_REPO,
    LANG_TASKS_URL,
    LANG_TASKS_LOCAL_REPO,
)


def red(msg):
    return click.style(msg, fg="red")


def green(msg):
    return click.style(msg, fg="green")


def remove_readonly(func, path, _):
    """
    A helper function for Windows that allows you to remove read only files
    from a .git directory
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def call_command(command, verbose=True, return_stdout=False, return_stderr=False):
    """
    The function invokes the specified command via subprocess and outputs
    stdout and stderr if the verbose flag is True.
    """
    result = subprocess.run(
        command,
        shell=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    std = result.stdout
    stderr = result.stderr
    if return_stdout:
        return std
    if return_stderr:
        return result.returncode, stderr
    if verbose:
        print("#" * 20, command)
        if std:
            print(std)
        if stderr:
            print(stderr)
    return result.returncode


def working_dir_clean():
    git_status = call_command("git status --porcelain", return_stdout=True)
    if git_status:
        return False
    else:
        return True


def show_git_diff_short():
    git_diff = call_command("git diff --stat")


def git_push(branch):
    """
    The function calls git push on Windows
    """
    command = f"git push origin {branch}"
    print("#" * 20, command)
    result = subprocess.run(command, shell=True)


def save_changes_to_github(
    message="All changes saved", git_add_all=True, branch="main"
):
    status = call_command("git status -s", return_stdout=True)
    if not status:
        return
    if git_add_all:
        call_command("git add .")
    call_command(f'git commit -m "{message}"')
    windows = True if system_name().lower() == "windows" else False

    if windows:
        git_push(branch)
    else:
        call_command(f"git push origin {branch}")


def current_chapter_id():
    """
    The function returns the number of the current task chapter where pyneng is
    called.
    """
    current_chapter_name = current_dir_name()
    if current_chapter_name in DB_TASK_DIRS:
        current_chapter_name = TASK_DIRS[-1]
    current_chapter = int(current_chapter_name.split("_")[0])
    return current_chapter


def current_dir_name():
    pth = str(pathlib.Path().absolute())
    current_chapter_name = os.path.split(pth)[-1]
    return current_chapter_name


def parse_json_report(report):
    """
    Selects the desired parts from the pytest run report in JSON format.
    Returns a list of tests that passed.
    """
    if report and report["summary"]["total"] != 0:
        all_tests = defaultdict(list)
        summary = report["summary"]

        test_names = [test["nodeid"] for test in report["collectors"][0]["result"]]
        for test in report["tests"]:
            name = test["nodeid"].split("::")[0]
            all_tests[name].append(test["outcome"] == "passed")
        all_passed_tasks = [name for name, outcome in all_tests.items() if all(outcome)]
        return all_passed_tasks
    else:
        return []


def git_clone_repo(repo_url, dst_dir):
    returncode, stderr = call_command(
        f"git clone {repo_url} {dst_dir}",
        verbose=False,
        return_stderr=True,
    )
    if returncode != 0:
        if "could not resolve host" in stderr.lower():
            raise PynengError(
                red(
                    "Failed to clone the repository. Maybe you don't have internet access?"
                )
            )
        else:
            raise PynengError(red(f"Failed to copy files. {stderr}"))


def copy_answers(passed_tasks):
    """
    The function clones the answer repository and copies the answers for tasks
    that pass the tests.
    """
    pth = str(pathlib.Path().absolute())
    current_chapter_name = os.path.split(pth)[-1]
    current_chapter_number = int(current_chapter_name.split("_")[0])

    homedir = pathlib.Path.home()
    os.chdir(homedir)
    if os.path.exists("pyneng-answers"):
        shutil.rmtree("pyneng-answers", onerror=remove_readonly)
    git_clone_repo(ANSWERS_URL, "pyneng-answers")
    os.chdir(os.path.join("pyneng-answers", "answers", current_chapter_name))
    copy_answer_files(passed_tasks, pth)
    print(
        green(
            "\nAnswers to tasks that passed the tests are copied to the files "
            "answer_task_x.py\n"
        )
    )
    os.chdir(homedir)
    shutil.rmtree("pyneng-answers", onerror=remove_readonly)
    os.chdir(pth)


def copy_answer_files(passed_tasks, pth):
    """
    The function copies the answers for the specified tasks.
    """
    for test_file in passed_tasks:
        task_name = test_file.replace("test_", "")
        task_name = re.search(r"task_\w+\.py", task_name).group()
        answer_name = test_file.replace("test_", "answer_")
        answer_name = re.search(r"answer_task_\w+\.py", answer_name).group()
        pth_answer = os.path.join(pth, answer_name)
        if not os.path.exists(pth_answer):
            shutil.copy2(task_name, pth_answer)


def clone_or_pull_task_repo():
    course_tasks_repo_dir = ".pyneng-course-tasks"
    source_pth = str(pathlib.Path().absolute())
    homedir = pathlib.Path.home()
    os.chdir(homedir)
    if os.path.exists(course_tasks_repo_dir):
        os.chdir(course_tasks_repo_dir)
        call_command("git pull")
        os.chdir(homedir)
    else:
        git_clone_repo(TASKS_URL, course_tasks_repo_dir)
    os.chdir(source_pth)


def copy_tasks_tests_from_repo(tasks, tests):
    """
    The function clones the repository with the latest version of tasks and
    copies the specified tasks to the current directory.
    """
    source_pth = str(pathlib.Path().absolute())
    current_chapter_name = os.path.split(source_pth)[-1]
    current_chapter_number = int(current_chapter_name.split("_")[0])

    clone_or_pull_task_repo()

    course_tasks_repo_dir = ".pyneng-course-tasks"
    homedir = pathlib.Path.home()
    os.chdir(
        os.path.join(homedir, course_tasks_repo_dir, "exercises", current_chapter_name)
    )
    copy_task_test_files(source_pth, tasks, tests)
    print(green("\nUpdated tasks and tests copied"))
    os.chdir(source_pth)


def copy_task_test_files(source_pth, tasks=None, tests=None):
    """
    The function copies task and test files.
    """
    file_list = []
    if tasks:
        file_list += tasks
    if tests:
        file_list += tests
    for file in file_list:
        shutil.copy2(file, os.path.join(source_pth, file))


def save_working_dir(branch="main"):
    if not working_dir_clean():
        print(
            red(
                "Updating tests and tasks will overwrite the contents of unsaved files!".upper()
            )
        )
        user_input = input(
            red(
                "There are unsaved changes in the current directory! "
                "Do you want to save them? [y/n]: "
            )
        )
        if user_input.strip().lower() not in ("n", "no"):
            save_changes_to_github(
                "Saving changes before updating tasks", branch=branch
            )
            print(
                green(
                    "All changes in the current directory are saved. Let's start updating..."
                )
            )


def working_dir_changed_diff(branch="main"):
    print(red("The following files have been updated:"))
    show_git_diff_short()
    print(
        "\nThis is a short diff, if you want to see all the differences in detail, "
        "press n and run git diff command.\nYou can also undo your changes with "
        "git checkout -- file (or git restore file) if you want."
    )

    user_input = input(red("\nSave changes and add to github? [y/n]: "))
    if user_input.strip().lower() not in ("n", "no"):
        save_changes_to_github("Updating tasks", branch=branch)


def change_tasks_lang(lang):
    global TASKS_URL
    global TASKS_LOCAL_REPO
    TASKS_URL = LANG_TASKS_URL.get(lang)
    TASKS_LOCAL_REPO = LANG_TASKS_LOCAL_REPO.get(lang)


def update_tasks_and_tests(tasks_list, tests_list, lang, branch="main"):
    change_tasks_lang(lang)
    save_working_dir(branch=branch)
    copy_tasks_tests_from_repo(tasks_list, tests_list)
    if working_dir_clean():
        print(green("Tasks and tests are already the latest version"))
        return False
    else:
        working_dir_changed_diff(branch=branch)
        return True


def update_chapters_tasks_and_tests(update_chapters, lang, branch="main"):
    change_tasks_lang(lang)
    save_working_dir(branch=branch)
    copy_chapters_from_repo(update_chapters)
    if working_dir_clean():
        print(green("All chapters are up to date"))
        return False
    else:
        working_dir_changed_diff(branch=branch)
        return True


def copy_chapters_from_repo(chapters_list):
    """
    The function clones the repository with the latest version of tasks and
    copies the specified tasks to the current directory.
    """
    source_pth = str(pathlib.Path().absolute())
    clone_or_pull_task_repo()

    course_tasks_repo_dir = ".pyneng-course-tasks"
    homedir = pathlib.Path.home()
    os.chdir(os.path.join(homedir, course_tasks_repo_dir, "exercises"))
    copy_chapters(source_pth, chapters_list)
    print(green("\nUpdated sections copied"))
    os.chdir(source_pth)


def copy_chapters(source_pth, chapters_list):
    """
    Function copies chapters
    """
    for chapter in chapters_list:
        to_path = os.path.join(source_pth, chapter)
        if os.path.exists(to_path):
            shutil.rmtree(to_path)
        shutil.copytree(chapter, to_path)
