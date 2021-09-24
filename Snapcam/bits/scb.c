#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <stdio.h>
#include "scb.h"

static PyObject *hello_world(PyObject *self, PyObject *args){
  if (!PyArg_ParseTuple(args, "y*", &data))
    return NULL;

  printf("hello world!\n");
  Py_RETURN_NONE;
}

static PyMethodDef scb_methods[] = {
  { "hello", hello_world, METH_VARARGS, NULL },
  { NULL, NULL, 0, NULL }
};

static struct PyModuleDef scb_module = {
  PyModuleDef_HEAD_INIT,
  "SnapcamBits",
  NULL,
  -1,
  scb_methods
};

PyMODINIT_FUNC PyInit_SnapcamBits(void){ return PyModule_Create(&scb_module); }
