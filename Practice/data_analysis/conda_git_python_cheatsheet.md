# Conda, Git & Python — Essential Command Reference

A working reference for daily use. Organized by category, roughly ordered from "use constantly" to "use occasionally."

---

## CONDA — Environment Management

### Daily use
```bash
conda activate mlenv              # activate an environment
conda deactivate                  # exit current environment back to base
conda env list                    # list all environments (shows which is active)
conda info --envs                 # same as above, alternate command
conda list                        # list packages installed in current env
conda list numpy                  # check if a specific package is installed
```

### Creating & removing environments
```bash
conda create -n myenv python=3.11         # create new env with specific Python version
conda create -n myenv python=3.11 numpy   # create env and install packages at once
conda create --clone mlenv -n mlenv2      # duplicate an existing environment
conda remove -n myenv --all               # delete an environment completely
conda rename -n oldname newname           # rename an environment
```

### Installing & removing packages
```bash
conda install numpy pandas         # install packages into active env
conda install numpy=1.26.0         # install a specific version
conda install -c conda-forge lib   # install from a specific channel
conda remove numpy                 # uninstall a package
conda update numpy                 # update a single package
conda update --all                 # update all packages in env (careful — see note below)
conda update conda                 # update conda itself
```

### Info & troubleshooting
```bash
conda --version                    # check conda version
conda info                         # show conda install details, paths, channels
which python                       # confirm which Python binary is active
python --version                   # confirm Python version in current env
conda list --revisions             # see history of changes to current env
conda install --revision 2         # roll back env to a previous revision
conda config --show channels       # see configured package channels
conda clean --all                  # clear cached package files, free disk space
```

### Exporting & sharing environments
```bash
conda env export > environment.yml            # export full env spec (for sharing)
conda env export --from-history > env.yml      # export only what you explicitly installed
conda env create -f environment.yml            # recreate an env from a yml file
```

> **Note:** Once you `pip install` something into a conda env, avoid `conda update --all` on that env — it can conflict with pip-managed packages. Prefer targeted updates instead.

---

## GIT — Version Control

### Setup (one-time)
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
git --version
```

### Starting a project
```bash
git init                           # turn current folder into a git repo
git clone <url>                    # copy a remote repo to your machine
git clone <url> myfolder           # clone into a custom folder name
```

### Daily workflow (the ones you'll use constantly)
```bash
git status                         # see what's changed / staged / untracked
git add file.py                    # stage a specific file
git add .                          # stage everything changed in current folder
git commit -m "message"            # commit staged changes with a message
git commit -am "message"           # stage + commit tracked files in one step
git push                           # send commits to remote (e.g. GitHub)
git pull                           # fetch + merge latest changes from remote
git log                            # view commit history
git log --oneline                  # compact one-line-per-commit history
git diff                           # see unstaged changes line-by-line
git diff --staged                  # see staged changes before committing
```

### Branching
```bash
git branch                         # list local branches
git branch feature-x               # create a new branch
git checkout feature-x             # switch to a branch
git checkout -b feature-x          # create AND switch in one command
git switch feature-x               # modern alternative to checkout
git switch -c feature-x            # modern alternative, create + switch
git merge feature-x                # merge a branch into current branch
git branch -d feature-x            # delete a branch (safe, only if merged)
git branch -D feature-x            # force-delete a branch
```

### Undoing things
```bash
git restore file.py                # discard unstaged changes to a file
git restore --staged file.py       # unstage a file (keep the changes)
git reset --soft HEAD~1            # undo last commit, keep changes staged
git reset --hard HEAD~1            # undo last commit, DELETE changes entirely
git revert <commit-hash>           # create a new commit that undoes a past one
git stash                          # temporarily shelve uncommitted changes
git stash pop                      # restore stashed changes
git stash list                     # see all stashed changes
```

### Remote repos
```bash
git remote -v                      # see linked remote repos
git remote add origin <url>        # link a remote repo
git fetch                          # download changes without merging
git push -u origin main            # push and set upstream tracking (first push)
git push origin --delete branch    # delete a branch on the remote
```

### Inspecting
```bash
git show <commit-hash>             # see details of a specific commit
git blame file.py                  # see who/when changed each line
git log --graph --oneline --all    # visualize branch history
```

---

## PYTHON — Core Language & Environment

### Running code
```bash
python script.py                   # run a script
python -i script.py                # run then drop into interactive shell
python -c "print('hello')"         # run inline code from terminal
python -m module_name               # run a module as a script
python -m venv myenv                # create a plain (non-conda) virtual env
```

### pip (package management inside an env)
```bash
pip install package                 # install a package
pip install package==1.2.0          # install specific version
pip install -r requirements.txt     # install from a requirements file
pip freeze > requirements.txt       # export installed packages to a file
pip list                            # list installed packages
pip show package                    # show details/version of a package
pip uninstall package               # remove a package
pip install --upgrade package       # upgrade a package
```

### Interactive / REPL basics
```python
help(function_name)                 # view documentation for a function
dir(object)                         # list attributes/methods of an object
type(variable)                      # check the type of a variable
id(variable)                        # memory address / identity of an object
```

### Common built-in functions (used constantly in data work)
```python
len(x)                              # length of a list/string/etc.
range(10)                           # generate a sequence of numbers
enumerate(list)                     # loop with index + value
zip(list1, list2)                   # pair up two iterables
sorted(list)                        # return a sorted copy
map(func, list)                     # apply function to every item
filter(func, list)                  # keep items where function is True
sum(list)                           # sum of numeric items
min(list) / max(list)               # smallest / largest item
isinstance(x, int)                  # check type of a variable
```

### File handling
```python
open("file.txt", "r")               # open file for reading
open("file.txt", "w")               # open file for writing (overwrites)
open("file.txt", "a")               # open file for appending
with open("file.txt") as f:         # preferred pattern — auto-closes file
    data = f.read()
```

### Debugging & inspection
```bash
python -m pdb script.py             # run script with debugger attached
```
```python
import pdb; pdb.set_trace()         # set a manual breakpoint in code
print(f"{variable=}")               # debug-print with variable name (Python 3.8+)
```

### Jupyter (since your books use notebooks heavily)
```bash
jupyter notebook                    # launch classic notebook interface
jupyter lab                         # launch JupyterLab interface
jupyter kernelspec list             # see which envs are available as kernels
python -m ipykernel install --user --name=mlenv   # register mlenv as a kernel
```

---

## Quick Daily Startup Routine

```bash
cd ~/Documents/PYTHON/Practice      # go to your working folder
conda activate mlenv                # activate your environment
git status                          # check what's changed since last session
jupyter lab                         # (optional) launch notebook interface
```

And when wrapping up:
```bash
git add .
git commit -m "describe what you did"
git push                            # if using a remote repo
conda deactivate
```
