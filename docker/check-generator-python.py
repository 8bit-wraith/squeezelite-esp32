"""Check the Python selected by nanopb's /usr/bin/env python3 shebang."""
import importlib
import shutil
import sys

print("Generator Python:", sys.executable, sys.version, flush=True)
print("PATH python:", shutil.which("python"), flush=True)
print("PATH python3:", shutil.which("python3"), flush=True)
missing = []
for name in ("google.protobuf", "grpc_tools.protoc", "pkg_resources"):
    try:
        module = importlib.import_module(name)
        print(name, getattr(module, "__file__", None), flush=True)
    except ImportError as error:
        print("{} unavailable: {}".format(name, error), flush=True)
        if name == "google.protobuf":
            missing.append(name)
if missing:
    sys.exit("Generator dependencies missing; firmware build not started.")
