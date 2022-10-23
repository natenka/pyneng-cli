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

