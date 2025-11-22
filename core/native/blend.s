    .file "blend.s"
    .text
    .globl _blend_signals
    .def _blend_signals; .scl 2; .type 32; .endef

# Function: blend_signals (C name) -> _blend_signals (Asm name)
# Calling Convention: cdecl (arguments on stack)
# Arguments:
#   [esp + 4]  : pid_out (double, 8 bytes)
#   [esp + 12] : mpc_out (double, 8 bytes)
#   [esp + 20] : alpha   (double, 8 bytes)
# Return:
#   st(0)      : result (double)

_blend_signals:
    # Formula: result = mpc + alpha * (pid - mpc)
    
    fldl    20(%esp)        # Load Alpha
    fldl    4(%esp)         # Load PID
    fsubl   12(%esp)        # st(0) = PID - MPC
    fmulp   %st, %st(1)     # st(0) = Alpha * (PID - MPC)
    faddl   12(%esp)        # st(0) = Alpha * (PID - MPC) + MPC
    
    ret
