#include <Python.h>
#include <unistd.h>

static PyObject* ls_reload(PyObject *self, PyObject *args) {
    int rtn_val = syscall(401);

    return Py_BuildValue("i", rtn_val);
}

static PyObject* ls_login(PyObject *self, PyObject *args) {
    int rtn_val = -EINVAL;
    char *passwd = "";

    if (!PyArg_ParseTuple(args, "s", &passwd))
        return Py_BuildValue("i", rtn_val);

    rtn_val = syscall(402, passwd);

    return Py_BuildValue("i", rtn_val);
}

static PyObject* ls_logout(PyObject *self, PyObject *args) {
    int rtn_val = syscall(403);

    return Py_BuildValue("i", rtn_val);
}

static struct PyMethodDef ls_methods[] = {
    {"ls_reload", ls_reload, METH_VARARGS},
    {"ls_login", ls_login, METH_VARARGS},
    {"ls_logout", ls_logout, METH_VARARGS},
    {NULL, NULL}
};

void initls_syscall() {
	Py_InitModule("ls_syscall", ls_methods);
}

