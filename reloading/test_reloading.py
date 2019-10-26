import unittest
import os
import subprocess as sp
import time

from reloading import reloading

SRC_FILE_NAME = 'temporary_testing_file.py'

TEST_CHANGING_SOURCE_CONTENT = '''
from reloading import reloading
from time import sleep

for epoch in reloading(range(10)):
    sleep(0.1)
    print('INITIAL_FILE_CONTENTS')
'''

TEST_KEEP_LOCAL_VARIABLES_CONTENT = '''
from reloading import reloading
from time import sleep

fpath = "DON'T CHANGE ME"
for epoch in reloading(range(1)):
    assert fpath == "DON'T CHANGE ME"
'''


def run_and_update_source(init_src, updated_src=None, update_after=0.2):
    '''Runs init_src in a subprocess and updated source to updated_src after
    update_after seconds. Returns the standard output of the subprocess.
    '''
    with open(SRC_FILE_NAME, 'w') as f:
        f.write(init_src)

    cmd = ['python', SRC_FILE_NAME]
    with sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE) as proc:
        if updated_src != None:
            time.sleep(update_after)
            with open(SRC_FILE_NAME, 'w') as f:
                f.write(updated_src)

        try:
            stdout, _ = proc.communicate(timeout=2)
            stdout = stdout.decode('utf-8')
            has_error = False
        except:
            stdout = ''
            has_error = True
            proc.terminate() 

    if os.path.isfile(SRC_FILE_NAME):
        os.remove(SRC_FILE_NAME)

    return stdout, has_error


class TestReloading(unittest.TestCase):

    def test_simple_looping(self):
        iters = 0
        for _ in reloading(range(10)):
            iters += 1

    def test_changing_source(self):
        stdout, _ = run_and_update_source(
          init_src=TEST_CHANGING_SOURCE_CONTENT,
          updated_src=TEST_CHANGING_SOURCE_CONTENT.replace('INITIAL', 'CHANGED').rstrip('\n'))

        self.assertTrue('INITIAL_FILE_CONTENTS' in stdout and
                        'CHANGED_FILE_CONTENTS' in stdout)

    def test_keep_local_variables(self):
        _, has_error = run_and_update_source(init_src=TEST_KEEP_LOCAL_VARIABLES_CONTENT)
        self.assertFalse(has_error)


if __name__ == '__main__':
    unittest.main()
