from distutils.core import setup, Extension

setup(
    name='ls_syscall',
    install_requires=[
        "urwid==1.3.0",
    ],
    ext_modules=[Extension('ls_syscall', ['ls_syscall.c'])]
)
