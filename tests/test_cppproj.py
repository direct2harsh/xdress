from __future__ import print_function

import os
import sys
import shutil
import subprocess
import tempfile

from nose.tools import assert_true, assert_equal

from xdress.astparsers import PARSERS_AVAILABLE

if sys.version_info[0] >= 3:
    basestring = str

PROJDIR = os.path.abspath("cppproj")
INSTDIR = os.path.join(PROJDIR, 'install')

def cleanfs():
    builddir = os.path.join(PROJDIR, 'build')
    if os.path.isdir(builddir):
        shutil.rmtree(builddir)
    if os.path.isdir(INSTDIR):
        shutil.rmtree(INSTDIR)

def check_cmd(args):
    if not isinstance(args, basestring):
        args = " ".join(args)
    print("TESTING: running command in {0}:\n\n{1}\n".format(PROJDIR, args))
    f = tempfile.NamedTemporaryFile()
    rtn = subprocess.call(args, shell=True, cwd=PROJDIR, stdout=f, stderr=f)
    if rtn != 0:
        f.seek(0)
        print("STDOUT + STDERR:\n\n" + f.read())
    f.close()
    assert_equal(rtn, 0)
    return rtn

# Because we want to guarentee build and test order, we can only have one 
# master test function which generates the individual tests.

def test_all():
    parsers = ['gccxml', 'clang']
    cases = [{'parsers': p} for p in parsers]

    cwd = os.getcwd()
    base = os.path.dirname(cwd)
    pyexec = sys.executable
    xdexec = os.path.join(base, 'scripts', 'xdress')

    cmds = [
        ['PYTHONPATH="{0}"'.format(base), pyexec, xdexec, '--debug'],
        [pyexec, 'setup.py', 'install', '--prefix="{0}"'.format(INSTDIR), '--', '--'],
        ]

    for case in cases:
        parser = case['parsers']
        if not PARSERS_AVAILABLE[parser]:
            continue
        cleanfs()
        rtn = 1
        for cmd in cmds:
            rtn = yield check_cmd, cmd
            if rtn != 0:
                break  # don't execute further commands
        if rtn != 0:
            break  # don't try further cases