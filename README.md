gdbprof
=======
A wall clock time-based profiler powered by GDB and its Python API. Heavily
inspired by [poor man's profiler](http://poormansprofiler.org/).

Rationale
---------
If there's something strange in your neighborhood (like X consuming 75% CPU in
`memcpy()` which `perf` can't trace), who you gonna call? `gdb`! Of course, if
you're lazy like me, you don't want to spend too much time hitting
<kbd>Ctrl</kbd>+<kbd>C</kbd>.

Caveats
-------
This is hack layered upon hack upon hack. See the source code if you want to
know how it "works". With the current state of gdb's Python affairs, it's
impossible to do it cleanly, but I think it's slightly better than an
expect-based approach because of the lower latency. **Use with CAUTION!**

Also, I recommend **attaching** to a running process, rather than starting it
from gdb. You'll need to hold down <kbd>Ctrl</kbd>+<kbd>C</kbd> to stop it if
you start it from `gdb`, as you need to interrupt `gdb`, not the process (I need
to handle this better).

Example
-------
```
(gdb) source gdbprof.py
(gdb) profile begin
..................................................^C
Profiling complete with 50 samples.
27      poll->None->None->xcb_wait_for_reply->_XReply->None->None->intel_update_renderbuffers->intel_prepare_render->None->None->None->None->None->None->None->None->None->None->None->None->__libc_start_main->None->None->None
10      nanosleep->usleep->None->None->None->None->__libc_start_main->None->None->None
4       poll->None->None->xcb_wait_for_reply->_XReply->None->None->intel_update_renderbuffers->intel_prepare_render->None->None->None->None->__libc_start_main->None->None->None
2       poll->None->None->xcb_wait_for_reply->_XReply->None->None->intel_update_renderbuffers->intel_prepare_render->None->None->None->None->None->None->None->None->None->None->None->None->None->None->__libc_start_main->None->None->None
1       gettimeofday->SDL_GetTicks->None->SDL_PumpEvents->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->__libc_start_main->None->None->None
1       recv->None->None->None->None->_XEventsQueued->XFlush->None->None->SDL_PumpEvents->SDL_PollEvent->None->None->__libc_start_main->None->None->None
1       poll->None->None->xcb_wait_for_reply->_XReply->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->__libc_start_main->None->None->None
1       ioctl->drmIoctl->None->_intel_batchbuffer_flush->intelFinish->None->None->None->None->None->None->__libc_start_main->None->None->None
1       poll->None->None->xcb_wait_for_reply->_XReply->None->None->intel_update_renderbuffers->intel_prepare_render->None->None->None->None->None->None->__libc_start_main->None->None->None
1       None->brw_upload_state->brw_draw_prims->vbo_exec_vtx_flush->None->vbo_exec_FlushVertices->_mesa_PolygonOffset->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->__libc_start_main->None->None->None
1       glDisable->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->None->__libc_start_main->None->None->None
(gdb)
```
