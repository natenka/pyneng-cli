DOCS = """
## Installation and launch

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

В заданиях и тестах встречаются неточности и чтобы их можно было исправить,
pyneng добавлена опция ``--update``.

Общая логика:

* задания и тесты копируются из репозитория https://github.com/pyneng/pyneng-course-tasks
* копируется весь файл задания, не только описание, поэтому файл перепишется
* перед выполнением --update, лучше сохранить все изменения на github

Как работает --update

* если в репозитории есть несохраненные изменения
  * утилита предлагает их сохранить (сделает ``git add .``, ``git commit``, ``git push``)
* если несохраненных изменений нет, копируются указанные задания и тесты
* утилита предлагает сохранить изменения и показывает какие файлы изменены, но не какие именно сделаны изменения
* можно отказаться сохранять изменения и посмотреть изменения git diff

#### Варианты вызова

Обновить все задания и тесты раздела:

```
pyneng --update
```

Обновить все тесты раздела (только тесты, не задания):

```
pyneng --update --test-only
```

Обновить задания 1,2 и соответствующие тесты раздела

```
pyneng 1,2 --update
```

Если никаких обновлений нет, будет такой вывод

```
$ pyneng --update
#################### git pull
Already up-to-date.


Обновленные задания и тесты скопированы
Задания и тесты уже последней версии
Aborted!
```

В любой момент можно прервать обновление Ctrl-C.

Пример вывода с несохраненными изменениями и наличием обновлений
```
pyneng --update
ОБНОВЛЕНИЕ ТЕСТОВ И ЗАДАНИЕ ПЕРЕЗАПИШЕТ СОДЕРЖИМОЕ НЕСОХРАНЕННЫХ ФАЙЛОВ!
В текущем каталоге есть несохраненные изменения! Хотите их сохранить? [y/n]: y
#################### git add .
#################### git commit -m "Сохранение изменений перед обновлением заданий"
[main 0e8c1cb] Сохранение изменений перед обновлением заданий
 1 file changed, 1 insertion(+)

#################### git push origin main
To git@github.com:pyneng/online-14-natasha-samoylenko.git
   fa338c3..0e8c1cb  main -> main

Все изменения в текущем каталоге сохранены. Начинаем обновление...
#################### git pull
Already up-to-date.


Обновленные задания и тесты скопированы
Были обновлены такие файлы:
#################### git diff --stat
 exercises/04_data_structures/task_4_0.py |  0
 exercises/04_data_structures/task_4_1.py |  1 -
 exercises/04_data_structures/task_4_3.py |  3 ---
 3 files changed, 0 insertions(+), 4 deletions(-)


Это короткий diff, если вы хотите посмотреть все отличия подробно, нажмите n и дайте команду git diff.
Также при желании можно отменить внесенные изменения git checkout -- file (или git restore file).

Сохранить изменения и добавить на github? [y/n]: n
Задания и тесты успешно обновлены
Aborted!
```
"""
