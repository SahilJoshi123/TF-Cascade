#!/usr/bin/python
import tfcascade_app as wp
import sys

if len(sys.argv) > 1:
    wp.test_run(int(sys.argv[1]))
else:
    wp.test_run()
