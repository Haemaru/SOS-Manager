import sys

PYPY = hasattr(sys, 'pypy_version_info')

try:
    from setuptools import Extension, setup
except ImportError:
    if PYPY:
        # need setuptools for include_package_data to work
        raise
    from distutils.core import Extension, setup

def install():
    setup(
        name='sos',
        version='0.1.7',
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
        scripts=['sos_manager'],
        install_requires=[
            "urwid==1.3.0",
        ],
        packages=['sos'],
        ext_modules=[Extension('ls_syscall', ['ls_syscall.c'])]
    )

if __name__ == '__main__':
    install()

