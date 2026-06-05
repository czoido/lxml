import os
import sys
import sysconfig

from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout


class LxmlConan(ConanFile):
    name = "lxml"
    version = "7.0.0a1"
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeToolchain", "CMakeDeps"

    def layout(self):
        cmake_layout(self, src_folder="..")

    def requirements(self):
        self.requires("libxslt/1.1.45")

    def configure(self):
        self.options["libxslt"].profiler = True

    def build(self):
        cmake = CMake(self)

        # Pin CMake to the exact Python running this build so it never
        # auto-detects a different arch/version from PATH or the Windows registry.
        # conanfile.py runs inside the isolated build-env venv, so sys.executable
        # and sys.base_prefix already point to the correct target Python.
        cli_args = [
            f"-DPython3_EXECUTABLE={sys.executable}",
            f"-DPython3_ROOT_DIR={sys.base_prefix}",
        ]
        if self.settings.os == "Windows":
            include_dir = sysconfig.get_path("include")
            lib_name = f"python{sys.version_info.major}{sys.version_info.minor}.lib"
            lib_path = os.path.join(sys.base_prefix, "libs", lib_name)
            cli_args += [f"-DPython3_INCLUDE_DIR={include_dir}"]
            if os.path.exists(lib_path):
                cli_args += [f"-DPython3_LIBRARY={lib_path}"]

        cmake.configure(cli_args=cli_args)
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
