from distutils.core import setup, Extension

setup(
    name='ls_syscall',
    version='0.1.0',
    license='MIT',
    description='SOS-Manager, Role based mandatory access control setup',
    long_description='',
    author='Haemaru',
    author_email='rkglskame01@gmail.com',
    url='https://github.com/Haemaru/SOS-Manager',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: Freeware',
        'Operation System :: POSIX'],
    scripts=['ls_tui'],
    install_requires=[
        "urwid==1.3.0",
    ],
    ext_modules=[Extension('ls_syscall', ['ls_syscall.c'])]
)
