## pyneng

Install module

```
pip install pyneng-cli
```

The task check is then invoked via the ``pyneng`` command in the CLI.


## Stages of working with tasks

1. Completing tasks
2. Checking that the task is working as it should python task_4_2.py or running the script in the editor/IDE
3. Checking tasks with pyneng 1-5
4. If the tests pass, we look at the solutions pyneng 1-5 -a

> The second step is very important because at this stage it is much easier to
> find syntax errors and similar problems with the script than when running the
> code through the test in stage 3.

## Checking tasks with tests

After completing the task, it can be checked using tests. To run the tests,
you need to call pyneng in the tasks directory. For example, if you are doing
chapter 4 tasks, you need to be in the exercises/04_data_structures/ directory
and run pyneng in one of the ways, depending on which tasks to check.

Run tests for all tasks in the current chapter:

```
pyneng
```

Running tests for task 4.1:

```
pyneng 1
```

Running tests for tasks 4.1, 4.2, 4.3:

```
pyneng 1-3
```

If there are tasks with letters, for example, in chapter 7, you can run it in
such a way as to run a check for tasks 7.2a, 7.2b (must be called in the
07_files directory):


```
pyneng 2a-b
```

or so to run all 7.2x tasks with and without letters:

```
pyneng 2*
```


## Getting answers to tasks

If the tasks pass the tests, you can see the answers (alternative solutions) of the tasks.

To do this, add ``-a`` to the previous command options. Such a call means to run
tests for tasks 1 and 2 and copy the answers if the tests pass:

```
pyneng 1-2 -a
```

Tests will run for the specified tasks, and for those tasks that pass the
tests, the answers will be copied to the answer_task_x.py files in the current
directory.

Answer files are not added to github by default. They can be:

* deleted
* added on github ``pyneng 1-3 -c --all`` (``--all`` adds all files in current directory and subdirectories git add . i.e. adds all file)
* added to .gitignore so that they are saved locally, but not saved in the repository. To do this, add the line ``answer_task*`` to the .gitignore file

It makes sense to add files to git if you write something in them. For example,
comments for yourself on some difficult points.

## Upload all changes in the current directory to github, regardless of whether the tests pass

```
pyneng --save-all
```

Executes commands

```
git add .
git commit -m "All changes saved"
git push origin main
```

## Chapter update

Pyneng has two options for updating: updating by chapters or by specific
tasks/tests. When a chapter is updated, the chapter's directory is deleted
and the new version is copied. This is only suitable for chapters that you
haven't started doing yet. If you need to update a specific task, it is better
to use the update of specific tasks (discussed later).

Before any upgrade option, it is advisable to save all local changes to github!

To update chapters, go to the your-repo/exercises/ directory and run the command:

```
pyneng --update-chapters 12-25
```

In this case, chapters 12-25 will be updated. You can also specify one chapter:

```
pyneng --update-chapters 11
```

Or several separated by commas

```
pyneng --update-chapters 12,15,17
```

## Update tasks and tests

There are inaccuracies in tasks and tests, and so that they can be corrected,
the ``--update`` option has been added to pyneng.

General logic:

* tasks and tests are copied from the repository
* the entire task file is copied, not just the description, so the file will be overwritten
* before doing --update, it's better to save all changes on github

How --update works

* if the repository has unsaved changes, pyneng offers to save them (does ``git add .``, ``git commit``, ``git push``)
* if there are no unsaved changes, the specified tasks and tests are copied
* the utility offers to save changes and shows which files have been changed, but not which changes have been made
* you can refuse to save the changes and see the changes git diff


#### Call Options

Update all tasks and tests of the section:

```
pyneng --update
```

Update all tests in a section (only tests, not tasks):

```
pyneng --update --test-only
```

Update tasks 1,2 and related section tests

```
pyneng 1,2 --update
```

If there are no updates, this will be the output

```
$ pyneng --update
#################### git pull
Already up-to-date.

Updated tasks and tests copied
tasks and tests are already the latest version
Aborted!
```

You can abort the update at any time with Ctrl-C.

Sample output with unsaved changes and updates
```
pyneng --update
THIS WILL OVERWRITE THE CONTENT OF UNSAVED FILES!
There are unsaved changes in the current directory! Do you want to save them? [y/n]:y
##################### git add .
#################### git commit -m "Save changes before updating tasks"
[main 0e8c1cb] Saving changes before updating tasks
 1 file changed, 1 insertion(+)

##################### git push origin main
To git@github.com:pyneng/my-tasks.git
   fa338c3..0e8c1cb main -> main

All changes in the current directory are saved. Let's start updating...
##################### git pull
Already up-to-date.


Updated tasks and tests copied
The following files have been updated:
##################### git diff --stat
 exercises/04_data_structures/task_4_0.py | 0
 exercises/04_data_structures/task_4_1.py | one -
 exercises/04_data_structures/task_4_3.py | 3---
 3 files changed, 0 insertions(+), 4 deletions(-)


This is a short diff, if you want to see all the differences in detail, press n and issue the git diff command.
You can also undo your changes with git checkout -- file (or git restore file) if you want.

Save changes and add to github? [y/n]:n
tasks and tests have been successfully updated
Aborted!
```
