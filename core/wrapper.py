import ctypes
import os
import sys

# Load the DLL
dll_path = os.path.join(os.path.dirname(__file__), 'native', 'controller.dll')
if not os.path.exists(dll_path):
    raise FileNotFoundError(f"Controller DLL not found at {dll_path}. Please run compile_native.bat first.")

try:
    _lib = ctypes.CDLL(dll_path)
except OSError as e:
    print(f"Error loading DLL: {e}")
    sys.exit(1)

# Define argument and return types
_lib.init_system.argtypes = []
_lib.init_system.restype = None

_lib.set_pid_params.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double]
_lib.set_pid_params.restype = None

_lib.get_position.argtypes = []
_lib.get_position.restype = ctypes.c_double

_lib.step_system.argtypes = [
    ctypes.c_double, # target
    ctypes.c_double, # dt
    ctypes.POINTER(ctypes.c_double), # out_pos
    ctypes.POINTER(ctypes.c_double), # out_u
    ctypes.POINTER(ctypes.c_double)  # out_alpha
]
_lib.step_system.restype = None

class NativeController:
    def __init__(self):
        self.init_system()
        
    def init_system(self):
        _lib.init_system()
        
    def set_pid_params(self, kp, ki, kd):
        _lib.set_pid_params(kp, ki, kd)
        
    def get_position(self):
        return _lib.get_position()
        
    def step(self, target, dt):
        out_pos = ctypes.c_double()
        out_u = ctypes.c_double()
        out_alpha = ctypes.c_double()
        
        _lib.step_system(target, dt, ctypes.byref(out_pos), ctypes.byref(out_u), ctypes.byref(out_alpha))
        
        return out_pos.value, out_u.value, out_alpha.value
