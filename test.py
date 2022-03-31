from ctypes import *
from os import read
import win32process

# getting process handle
openproc = windll.kernel32.OpenProcess

openproc.argtypes = (c_int,c_bool,c_int)
openproc.restype = c_void_p

process_handle = openproc(0x0010,0,12888)

print(process_handle)



# reading process memory
# 140700765782016
# 0x7ff7732a0000
readproc_memory = windll.kernel32.ReadProcessMemory

readproc_memory.restype = c_bool
readproc_memory.argtypes = (c_void_p,c_void_p,c_void_p,c_size_t,POINTER(c_size_t))

out = c_ulonglong()
size = c_size_t(100)
address = 0x7ff7732a0000
readproc_memory(process_handle,address,byref(out),size,byref(size))

print(hex(out.value))
