from distutils.core import setup, Extension

setup(
    name='ls_syscall',
    ext_modules=[Extension('ls_syscall', ['ls_syscall.c'])]
)
