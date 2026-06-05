cmake_minimum_required(VERSION 3.15)
project(lxml LANGUAGES C)

find_package(Python3 REQUIRED COMPONENTS Interpreter Development.Module)
find_package(LibXml2 REQUIRED)
find_package(LibXslt REQUIRED)

get_filename_component(_py_bin_dir ${Python3_EXECUTABLE} DIRECTORY)
find_program(CYTHON_EXECUTABLE NAMES cython cython3
    HINTS ${_py_bin_dir}
    REQUIRED
)

set(LXML_SRC_DIR ${CMAKE_CURRENT_SOURCE_DIR}/src/lxml)

# Generate lxml-version.h from __init__.py ("7.0.0a1" -> "7.0.0.alpha1")
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/src/lxml/__init__.py" _init_py)
string(REGEX MATCH "__version__ = \"([^\"]+)\"" _m "${_init_py}")
set(_lxml_ver "${CMAKE_MATCH_1}")
string(REPLACE "a" ".alpha" _lxml_ver "${_lxml_ver}")
string(REPLACE "b" ".beta"  _lxml_ver "${_lxml_ver}")
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/lxml-version.h"
    "#ifndef LXML_VERSION_STRING\n"
    "#define LXML_VERSION_STRING \"${_lxml_ver}\"\n"
    "#endif\n"
)

function(cython_add_module target pyx_file)
    get_filename_component(module_name ${pyx_file} NAME_WE)
    set(c_file ${CMAKE_CURRENT_BINARY_DIR}/${module_name}.c)

    add_custom_command(
        OUTPUT ${c_file}
        BYPRODUCTS
            ${CMAKE_CURRENT_BINARY_DIR}/${module_name}.h
            ${CMAKE_CURRENT_BINARY_DIR}/${module_name}_api.h
        COMMAND ${CYTHON_EXECUTABLE}
                -I ${CMAKE_CURRENT_SOURCE_DIR}/src
                ${pyx_file}
                --output-file ${c_file}
        DEPENDS ${pyx_file}
        COMMENT "Cythonizing ${module_name}.pyx"
        VERBATIM
    )

    Python3_add_library(${target} MODULE ${c_file})
    target_include_directories(${target} PRIVATE
        ${LXML_SRC_DIR}
        ${LXML_SRC_DIR}/includes
        ${CMAKE_CURRENT_BINARY_DIR}
    )
    target_link_libraries(${target} PRIVATE LibXml2::LibXml2 LibXslt::LibXslt)
    if(TARGET LibXslt::LibExslt)
        target_link_libraries(${target} PRIVATE LibXslt::LibExslt)
    endif()
    # Cython-generated code uses deprecated symbols and implicit function declarations
    # that clang 16+ treats as hard errors in C99 mode regardless of -w.
    target_compile_options(${target} PRIVATE
        -Wno-implicit-function-declaration
        -Wno-int-conversion
        -Wno-deprecated-declarations
    )
    set_target_properties(${target} PROPERTIES OUTPUT_NAME ${module_name})
    if(APPLE)
        set_target_properties(${target} PROPERTIES
            LINK_FLAGS "-undefined dynamic_lookup"
        )
    endif()
endfunction()

cython_add_module(etree     ${LXML_SRC_DIR}/etree.pyx)
cython_add_module(objectify ${LXML_SRC_DIR}/objectify.pyx)

# objectify.c includes etree_api.h, generated as a byproduct of the etree Cython step
add_dependencies(objectify etree)

install(TARGETS etree objectify DESTINATION lxml)
