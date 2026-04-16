# Ashes of Heroes | A game project in OpenGL

## Development setup

> [!IMPORTANT]\
> This applications runs **Python 3.14.3**.

> [!NOTE]\
> Assuming your environment is Linux, the following steps are completely valid.
> However, if it is not, **please refer to the link at the end of the section**.

First, create Python virtual enviroment using the following command:

```bash
python -m venv <env-directory>

# for example, something like...
python -m venv .venv
```

Immediately after that, activate the virtual environment with the command `source ./<env-directory>/bin/activate` to ensure that no dependencies are persistently installed on your machine.

Then, install the dependencies:

```bash
pip install --require-virtualenv -r requirements.txt
```

Finally, don't forget to disable your virtual environment (venv) when you finish your task.

```bash
# with just one command...
deactivate
```

> [!TIP]\
> If you have any questions, please consult:
> [(Python Land) Python venv: How To Create, Activate, Deactivate, And Delete](https://python.land/virtual-environments/virtualenv#google_vignette)

## A little about the project

...

## A little about the game

...

## Project structure

```text
.
├── assets
├── docs
│   └── lore
├── main.py
├── README.md
├── requirements.txt
├── shaders
└── src
    ├── core
    ├── graphics
    ├── logic
    └── utils

10 directories, 3 files
```
