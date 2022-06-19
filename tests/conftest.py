import os

if os.getenv("TEST_PGI"):
    import pgi

    pgi.install_as_gi()
    pgi.set_backend("ctypes,null")
