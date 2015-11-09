#include <Python.h>
#include <unistd.h>

static PyObject* ls_login(PyObject *self, PyObject *args)
{
    syscall(402)
}

static PyObjedt* ls_reload(PyObject *self, PyObject *args)
{
    syscall(401)
}

static struct PyMethodDef ls_methods[] = {
    {"ls_login", ls_login, METH_VARARGS},
    {"ls_reload", ls_reload, METH_VARARGS},
    {NULL, NULL}
};

