#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

class MongoCDriverConan(ConanFile):
    name = "mongo-c-driver"
    version = "1.11.0"
    description = "A high-performance MongoDB driver for C"
    url = "https://github.com/mongodb/mongo-c-driver"
    license = "https://github.com/mongodb/mongo-c-driver/blob/{0}/COPYING".format(version)
    settings =  "os", "compiler", "arch", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    requires = 'zlib/[~=1.2]@conan/stable'
    exports_sources = ["Find*.cmake", "header_path.patch"]
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"

    def configure(self):
        # Because this is pure C
        del self.settings.compiler.libcxx

    def requirements(self):
        if not tools.os_info.is_macos and not tools.os_info.is_windows:
            self.requires.add("OpenSSL/1.0.2n@conan/stable")

    def source(self):
        tools.get("https://github.com/mongodb/mongo-c-driver/releases/download/{0}/mongo-c-driver-{0}.tar.gz".format(self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)
        tools.patch(base_path=self.source_subfolder, patch_file="header_path.patch")

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            # self.build_vs()
            self.output.fatal("No windows support yet. Sorry. Help a fellow out and contribute back?")

        cmake = CMake(self)
        cmake.definitions["ENABLE_STATIC"] = "OFF" if self.options.shared else "ON"
        cmake.definitions["ENABLE_TESTS"] = False
        cmake.definitions["ENABLE_EXAMPLES"] = False
        cmake.definitions["ENABLE_AUTOMATIC_INIT_AND_CLEANUP"] = False
        cmake.definitions["ENABLE_BSON"] = "ON"

        if self.settings.os != 'Windows':
            cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = True
            #cmake.definitions['CMAKE_POSITION_INDEPENDENT_CODE'] = self.options.fPIC

        cmake.configure(build_folder=self.build_subfolder, source_folder=self.source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="COPYING*", src="sources")
        self.copy("Find*.cmake", ".", ".")
        # cmake installs all the files

    def package_info(self):
        self.cpp_info.libs = ["bson-1.0", "mongoc-1.0"] if self.options.shared else ["bson-static-1.0", "mongoc-static-1.0"]

        if tools.os_info.is_macos:
            self.cpp_info.exelinkflags = ['-framework CoreFoundation', '-framework Security']
            self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
        if tools.os_info.is_linux:
            self.cpp_info.libs.append("rt")
        if not tools.os_info.is_windows:
            self.cpp_info.libs.append("pthread")
