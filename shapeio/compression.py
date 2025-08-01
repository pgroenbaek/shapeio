import clr
import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path


def check_dependencies():
    system = platform.system()

    if system == "Linux" or system == "Darwin":
        if not shutil.which("mono"):
            raise EnvironmentError(
                "Mono is required to compress and decompress shapes but was not found.\n"
                "Install it via: sudo apt install mono-complete (Linux)\n"
                "Or: brew install mono (macOS)"
            )
    elif system == "Windows":
        try:
            output = subprocess.check_output(["reg", "query", "HKLM\\SOFTWARE\\Microsoft\\NET Framework Setup\\NDP\\v4\\Full"], stderr=subprocess.DEVNULL)
            if b"Install" not in output:
                raise EnvironmentError("Required .NET Framework not detected. Unable to compress and decompress shapes.")
        except Exception:
            raise EnvironmentError(
                "The .NET Framework is required to compress and decompress shapes, but it was not found.\n"
                "Install it from: https://dotnet.microsoft.com/en-us/download/dotnet-framework"
            )
    else:
        raise EnvironmentError(f"Unsupported OS: {system}")


def load_tk_utils_dll(tk_utils_dll_path: str):
    dll_path = Path(tk_utils_dll_path)

    if not dll_path.exists():
        raise FileNotFoundError(f".NET DLL not found at: {dll_path}")

    sys.path.append(str(dll_path.parent))
    if platform.system() != "Windows":
        os.environ["MONO_PATH"] = str(dll_path.parent)

    try:
        clr.AddReference(str(dll_path.stem))
    except Exception as e:
        raise ImportError(
            f"Could not load .NET DLL '{dll_path.name}'.\n"
            "Make sure Mono (Linux/macOS) or .NET Framework (Windows) is installed."
        ) from e

    from TK.MSTS.Tokens import TokenFileHandler
    return TokenFileHandler()


def compress_shape(input_path: str, output_path: str, tk_utils_dll_path: str) -> bool:
    check_dependencies()
    handler = load_tk_utils_dll(tk_utils_dll_path)
    return handler.Compress(input_path, output_path)


def decompress_shape(input_path: str, output_path: str, tk_utils_dll_path: str) -> bool:
    check_dependencies()
    handler = load_tk_utils_dll(tk_utils_dll_path)
    return handler.Decompress(input_path, output_path)