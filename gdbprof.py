# -*- coding: utf-8 -*-
# Copyright (c) 2012 Mak Nazečić-Andrlon
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import gdb
from collections import defaultdict
from time import sleep
import os
import signal


def get_call_chain():
    function_names = []
    frame = gdb.newest_frame()
    while frame is not None:
        function_names.append(frame.name())
        frame = frame.older()

    return tuple(function_names)


class ProfileCommand(gdb.Command):
    """Wall clock time profiling leveraging gdb for better backtraces."""

    def __init__(self):
        super(ProfileCommand, self).__init__("profile", gdb.COMMAND_RUNNING,
                                             gdb.COMPLETE_NONE, True)


class ProfileBeginCommand(gdb.Command):
    """Profile an application against wall clock time.
profile begin [PERIOD]
PERIOD is the sampling interval in seconds.
The default PERIOD is 0.5 seconds.
    """

    def __init__(self):
        super(ProfileBeginCommand, self).__init__("profile begin",
                                                  gdb.COMMAND_RUNNING)

    def invoke(self, argument, from_tty):
        self.dont_repeat()

        period = 0.5

        args = gdb.string_to_argv(argument)

        if len(args) > 0:
            try:

                period = int(args[0])
            except ValueError:
                gdb.write("Invalid number \"%s\"" % args[0])
                return

        def breaking_continue_handler(event):
            sleep(period)
            os.kill(gdb.selected_inferior().pid, signal.SIGINT)

        call_chain_frequencies = defaultdict(int)
        sleeps = 0

        try:
            gdb.events.cont.connect(breaking_continue_handler)
            while True:
                gdb.execute("continue", to_string=True)
                call_chain_frequencies[get_call_chain()] += 1
                sleeps += 1
                gdb.write(".")
                gdb.flush(gdb.STDOUT)
        except KeyboardInterrupt:
            pass
        finally:
            gdb.events.cont.disconnect(breaking_continue_handler)

        pid = gdb.selected_inferior().pid
        gdb.execute("detach", to_string=True)
        gdb.execute("attach %d" % pid, to_string=True)

        gdb.write("\nProfiling complete in %d samples.\n" % sleeps)
        for call_chain, frequency in sorted(call_chain_frequencies.iteritems(), key=lambda x: x[1], reverse=True):
            gdb.write("%d\t%s\n" % (frequency, '->'.join(str(i) for i in call_chain)))

ProfileCommand()
ProfileBeginCommand()
