from ls_syscall import ls_login, ls_logout


def login(passwd):
    ls_login(passwd)

def logout():
    ls_logout()

