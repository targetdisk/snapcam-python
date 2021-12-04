#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdbool.h>
#include <stdio.h>
#include <structmember.h>
#include "scb.h"

static PyObject *hello_world(PyObject *self){
  printf("hello world!\n");
  Py_RETURN_NONE;
}

static PyObject *pymcall_test(PyObject *self, PyObject *args){
  PyObject *hello_obj = NULL;

  if (!PyArg_ParseTuple(args, "O", &hello_obj)){
    goto mcall_error;
  }

  if (hello_obj == NULL)
    goto mcall_error;

  {
    PyObject *callme = PyUnicode_FromString("hello");
    if (callme == NULL) {
        Py_XDECREF(callme);
        goto mcall_error;
    }
    PyObject_CallMethodNoArgs(hello_obj, callme);
    Py_DECREF(callme);
  }

  Py_DECREF(hello_obj);
  Py_RETURN_NONE;

mcall_error:
  Py_XDECREF(hello_obj);
  return NULL;
}

static PyObject *queue_test(PyObject *self, PyObject *args){
  bool error = false;
  PyObject *pkt_queue = NULL;
  PyObject *test_queue = NULL;
  Py_buffer *pkt_b = NULL;

  if (!PyArg_ParseTuple(args, "OO", &pkt_queue, &test_queue)){
    goto queue_test_error;
  }

  {
    PyObject *callme = PyUnicode_FromString("get");
    pkt_b = PyObject_CallMethodNoArgs(pkt_queue, callme);
  }

  if (PyObject_CheckBuffer(pkt_b) == 1) {
    puts("is buffer");
  } else {
    puts("is not buffer?");
  }

  goto queue_test_cleanup;

queue_test_error:
  error = true;

queue_test_cleanup:
  PyBuffer_Release(pkt_b);
  Py_XDECREF(pkt_queue);
  Py_XDECREF(test_queue);

  if (error) {
    return NULL;
  } else {
    Py_RETURN_NONE;
  }
}

static PyMethodDef scb_methods[] = {
  { "hello_world", hello_world, METH_NOARGS, NULL },
  { "queue_test", queue_test, METH_VARARGS, NULL },
  { "mcall_test", pymcall_test, METH_VARARGS, NULL },
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
