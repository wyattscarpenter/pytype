#!/usr/bin/env python
"""A simple script to run CI build steps."""

import collections
import os
import shlex
import sys

import build_utils


STEP = collections.namedtuple("STEP", ["name", "command"])


def _begin_step(s):
  print("")
  if os.getenv("GITHUB_ACTIONS"):
    print(f"::group::{s.name}")
  else:
    print(f"BEGIN_STEP: {s.name}")
  print(f"Command: {shlex.join(s.command)}")
  print(flush=True)


def _end_step(s):
  print("")
  if os.getenv("GITHUB_ACTIONS"):
    print("::endgroup::")
  else:
    print(f"END_STEP: {s.name}")
  print(flush=True)


def _report_failure(s):
  print("")
  if os.getenv("GITHUB_ACTIONS"):
    print(f"::error::STEP FAILED: {s.name}")
  else:
    print(f">>> STEP_FAILED: {s.name}")
  print(flush=True)


def _run_steps(steps):
  exit_with_error: bool = False
  for s in steps:
    _begin_step(s)
    try:
      returncode, _ = build_utils.run_cmd(s.command, pipe=False)
      if returncode != 0:
        _report_failure(s)
        exit_with_error = True
    finally:
      _end_step(s)
  if exit_with_error:
    sys.exit(1)


def main():
  arguments = sys.argv[1:] #alternate way to call this program, with index arguments. See below.
  s1 = STEP(
      name="Lint",
      command=[
          "pylint",
          "build_scripts/",
          "pytype/",
          "pytype_extensions/",
          "setup.py",
      ],
  )
  s2 = STEP(
      name="Build", command=["python", build_utils.build_script("build.py")]
  )
  s3 = STEP(
      name="Run Tests",
      command=["python", build_utils.build_script("run_tests.py"), "-v"],
  )
  s4 = STEP(
      name="Run Extensions Tests",
      command=["python", "-m", "pytype_extensions.test_pytype_extensions"],
  )
  s5 = STEP(
      name="Type Check",
      command=(["python"] if sys.platform == "win32" else [])
      + [os.path.join("out", "bin", "pytype"), "-j", "auto"],
  )
  steps = [s1, s2, s3, s4, s5]
  if os.environ.get("LINT") == "false":
    steps.remove(s1)
  if not arguments:
    _run_steps(steps)
  else:
    for argument in arguments:
      index = int(argument)
      if index < len(arguments)
        
  print("\n*** All build steps completed successfully! ***\n")


if __name__ == "__main__":
  main()
