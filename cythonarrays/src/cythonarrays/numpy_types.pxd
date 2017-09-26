"""
Defines Ctype names to be used in cython modules

Attributes
----------
numpy array dtype in cython

    BTYPE_t
    DTYPE_i1_t ... DTYPE_i8_t
    DTYPE_u1_t ... DTYPE_u8_t
    DTYPE_f_t
    DTYPE_d_t

Arrays/Memoryviews

    ARRAY_1D_d ... ARRAY_5D_d
    ARRAY_1D_f ... ARRAY_5D_f

    ARRAY_1D_i1 ... ARRAY_3D_i1
    ARRAY_1D_i1 ... ARRAY_3D_i1
    ARRAY_1D_i4 ... ARRAY_3D_i4
    ARRAY_1D_i8 ... ARRAY_3D_i8
    ARRAY_1D_u1 ... ARRAY_3D_u1
    ...
    ARRAY_1D_u8 ... ARRAY_3D_u8

"""

cimport cython
cimport numpy as np

ctypedef cython.int long32

ctypedef cython.uint ulong32

ctypedef cython.char BTYPE_t

ctypedef cython.longlong DTYPE_i8_t

ctypedef cython.ulonglong DTYPE_u8_t

ctypedef cython.double DTYPE_d_t

ctypedef cython.float DTYPE_f_t

ctypedef cython.char DTYPE_i1_t

ctypedef cython.uint DTYPE_u4_t

ctypedef cython.short DTYPE_i2_t

ctypedef cython.uchar DTYPE_u1_t

ctypedef cython.int DTYPE_i4_t

ctypedef cython.ushort DTYPE_u2_t

ctypedef cython.ssize_t Pointer

ctypedef cython.double[:, :, :, : , :] ARRAY_5D_d
ctypedef cython.double[:, :, :, :] ARRAY_4D_d
ctypedef cython.double[:, :, :] ARRAY_3D_d
ctypedef cython.double[:, :] ARRAY_2D_d
ctypedef cython.double[:] ARRAY_1D_d

ctypedef cython.float[:, :, :, : , :] ARRAY_5D_f
ctypedef cython.float[:, :, :, :] ARRAY_4D_f
ctypedef cython.float[:, :, :] ARRAY_3D_f
ctypedef cython.float[:, :] ARRAY_2D_f
ctypedef cython.float[:] ARRAY_1D_f

ctypedef cython.char[:] ARRAY_1D_b
ctypedef cython.char[:] ARRAY_1D_i1
ctypedef cython.short[:] ARRAY_1D_i2
ctypedef cython.int[:] ARRAY_1D_i4
ctypedef cython.longlong[:] ARRAY_1D_i8
ctypedef cython.ssize_t[:] ARRAY_1D_Ptrs

ctypedef cython.char[:, :] ARRAY_2D_b
ctypedef cython.char[:, :] ARRAY_2D_i1
ctypedef cython.short[:, :] ARRAY_2D_i2
ctypedef cython.int[:, :] ARRAY_2D_i4
ctypedef cython.longlong[:, :] ARRAY_2D_i8

ctypedef cython.char[:, :, :] ARRAY_3D_b
ctypedef cython.char[:, :, :] ARRAY_3D_i1
ctypedef cython.short[:, :, :] ARRAY_3D_i2
ctypedef cython.int[:, :, :] ARRAY_3D_i4
ctypedef cython.longlong[:, :, :] ARRAY_3D_i8

ctypedef cython.char[:, :, :, :] ARRAY_4D_i1
ctypedef cython.char[:, :, :, :, :] ARRAY_5D_i1
ctypedef cython.int[:, :, :, :] ARRAY_4D_i4

ctypedef cython.uchar[:] ARRAY_1D_u1
ctypedef cython.ushort[:] ARRAY_1D_u2
ctypedef cython.uint[:] ARRAY_1D_u4
ctypedef cython.ulonglong[:] ARRAY_1D_u8

ctypedef cython.uchar[:, :] ARRAY_2D_u1
ctypedef cython.ushort[:, :] ARRAY_2D_u2
ctypedef cython.uint[:, :] ARRAY_2D_u4
ctypedef cython.ulonglong[:, :] ARRAY_2D_u8

ctypedef cython.uchar[:, :, :] ARRAY_3D_u1
ctypedef cython.ushort[:, :, :] ARRAY_3D_u2
ctypedef cython.uint[:, :, :] ARRAY_3D_u4
ctypedef cython.ulonglong[:, :, :] ARRAY_3D_u8

ctypedef fused np_signed_int:
    cython.char
    cython.short
    cython.int
    cython.longlong

ctypedef fused np_int_4_8:
    cython.int
    cython.longlong

ctypedef fused np_uint:
    cython.uchar
    cython.ushort
    cython.uint
    cython.ulonglong

ctypedef fused np_floating:
    cython.float
    cython.double

ctypedef fused np_integer:
    cython.char
    cython.short
    cython.int
    cython.longlong
    cython.uchar
    cython.ushort
    cython.uint
    cython.ulonglong

ctypedef fused np_numeric:
    cython.char
    cython.short
    cython.int
    cython.longlong
    cython.uchar
    cython.ushort
    cython.uint
    cython.ulonglong
    cython.float
    cython.double


ctypedef np_signed_int[:] ARRAY_1D_i
ctypedef np_int_4_8[:] ARRAY_1D_int
ctypedef np_uint[:] ARRAY_1D_u
ctypedef np_integer[:] ARRAY_1D_iu
ctypedef np_floating[:] ARRAY_1D_fd
ctypedef np_numeric[:] ARRAY_1D_n

ctypedef np_signed_int[:, :] ARRAY_2D_i
ctypedef np_int_4_8[:, :] ARRAY_2D_int
ctypedef np_uint[:, :] ARRAY_2D_u
ctypedef np_integer[:, :] ARRAY_2D_iu
ctypedef np_floating[:, :] ARRAY_2D_fd
ctypedef np_numeric[:, :] ARRAY_2D_n

ctypedef np_signed_int[:, :, :] ARRAY_3D_i
ctypedef np_int_4_8[:, :, :] ARRAY_3D_int
ctypedef np_uint[:, :, :] ARRAY_3D_u
ctypedef np_integer[:, :, :] ARRAY_3D_iu
ctypedef np_floating[:, :, :] ARRAY_3D_fd
ctypedef np_numeric[:, :, :] ARRAY_3D_n

ctypedef np_signed_int[:, :, :, :] ARRAY_4D_i
ctypedef np_int_4_8[:, :, :, :] ARRAY_4D_int
ctypedef np_uint[:, :, :, :] ARRAY_4D_u
ctypedef np_integer[:, :, :, :] ARRAY_4D_iu
ctypedef np_floating[:, :, :, :] ARRAY_4D_fd
ctypedef np_numeric[:, :, :, :] ARRAY_4D_n

ctypedef np_signed_int[:, :, :, :, :] ARRAY_5D_i
ctypedef np_int_4_8[:, :, :, :, :] ARRAY_5D_int
ctypedef np_uint[:, :, :, :, :] ARRAY_5D_u
ctypedef np_integer[:, :, :, :, :] ARRAY_5D_iu
ctypedef np_floating[:, :, :, :, :] ARRAY_5D_fd
ctypedef np_numeric[:, :, :, :, :] ARRAY_5D_n
