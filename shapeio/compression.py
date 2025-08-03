"""
This file is part of ShapeIO.

Copyright (C) 2025 Peter Grønbæk Andersen <peter@grnbk.io>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import clr
import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path


def check_dependencies():
    """
    Checks for required runtime dependencies based on the current operating system.

    - On Linux and macOS, verifies that the Mono runtime is installed.
      Raises an EnvironmentError if 'mono' is not found in the system path.
    
    - On Windows, checks for the presence of the .NET Framework 4.0 or later
      by querying the Windows Registry. Raises an EnvironmentError if it is missing.
    
    Raises:
        EnvironmentError: If the required runtime (Mono or .NET Framework) is not found,
                          or if the operating system is unsupported.
    """
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


def load_tkutils_dll(tkutils_dll_path: str):
    """
    Loads the TK.MSTS.Tokens .NET DLL and returns a TokenFileHandler instance.

    Args:
        tkutils_dll_path (str): The file path to the TK.MSTS.Tokens DLL.

    Raises:
        FileNotFoundError: If the specified DLL file does not exist.
        ImportError: If the DLL cannot be loaded, possibly due to missing Mono or .NET Framework.

    Returns:
        TokenFileHandler: An instance of the TokenFileHandler class from the loaded DLL.
    """
    dll_path = Path(tkutils_dll_path)

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


def compress_shape(input_path: str, output_path: str, tkutils_dll_path: str) -> bool:
    """
    Compresses a shape file using the TK.MSTS.Tokens DLL.

    Args:
        input_path (str): Path to the uncompressed input shape file.
        output_path (str): Path where the compressed shape file will be saved.
        tkutils_dll_path (str): Path to the TK.MSTS.Tokens DLL.

    Raises:
        EnvironmentError: If required runtime dependencies are missing.
        FileNotFoundError: If the DLL cannot be found.
        ImportError: If the DLL cannot be loaded.

    Returns:
        bool: True if compression succeeded, False otherwise.
    """
    check_dependencies()
    handler = load_tkutils_dll(tkutils_dll_path)
    return handler.Compress(input_path, output_path)


def decompress_shape(input_path: str, output_path: str, tkutils_dll_path: str) -> bool:
    """
    Decompresses a shape file using the TK.MSTS.Tokens DLL.

    Args:
        input_path (str): Path to the compressed input shape file.
        output_path (str): Path where the decompressed shape file will be saved.
        tkutils_dll_path (str): Path to the TK.MSTS.Tokens DLL.

    Raises:
        EnvironmentError: If required runtime dependencies are missing.
        FileNotFoundError: If the DLL cannot be found.
        ImportError: If the DLL cannot be loaded.

    Returns:
        bool: True if decompression succeeded, False otherwise.
    """
    check_dependencies()
    handler = load_tkutils_dll(tkutils_dll_path)
    return handler.Decompress(input_path, output_path)

