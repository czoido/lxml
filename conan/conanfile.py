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
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
