from ls_syscall import ls_login, ls_logout


def login(passwd):
    return ls_login(passwd)

def logout():
    return ls_logout()

