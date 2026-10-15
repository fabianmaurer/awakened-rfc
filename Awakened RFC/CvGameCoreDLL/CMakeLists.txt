cmake_minimum_required(VERSION 3.24)

project(RFCMPCvGameCoreDLL LANGUAGES CXX)

if(NOT MSVC)
	message(FATAL_ERROR "This project currently supports the Microsoft C++ compiler only.")
endif()

if(NOT CMAKE_SIZEOF_VOID_P EQUAL 4)
	message(FATAL_ERROR "Civilization IV Beyond the Sword requires a 32-bit DLL. Configure with -A Win32.")
endif()

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")

set(BOOST_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/Boost-1.32.0")
set(PYTHON24_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/Python24")
set(BOOST_PYTHON_SRC "${BOOST_ROOT}/libs/python/src")
set(BOOST_PYTHON_SOURCES
	${BOOST_PYTHON_SRC}/aix_init_module.cpp
	${BOOST_PYTHON_SRC}/converter/arg_to_python_base.cpp
	${BOOST_PYTHON_SRC}/converter/builtin_converters.cpp
	${BOOST_PYTHON_SRC}/object/class.cpp
	${BOOST_PYTHON_SRC}/dict.cpp
	${BOOST_PYTHON_SRC}/object/enum.cpp
	${BOOST_PYTHON_SRC}/errors.cpp
	${BOOST_PYTHON_SRC}/converter/from_python.cpp
	${BOOST_PYTHON_SRC}/object/function.cpp
	${BOOST_PYTHON_SRC}/object/inheritance.cpp
	${BOOST_PYTHON_SRC}/object/iterator.cpp
	${BOOST_PYTHON_SRC}/object/life_support.cpp
	${BOOST_PYTHON_SRC}/list.cpp
	${BOOST_PYTHON_SRC}/long.cpp
	${BOOST_PYTHON_SRC}/module.cpp
	${BOOST_PYTHON_SRC}/numeric.cpp
	${BOOST_PYTHON_SRC}/object_operators.cpp
	${BOOST_PYTHON_SRC}/object_protocol.cpp
	${BOOST_PYTHON_SRC}/object/pickle_support.cpp
	${BOOST_PYTHON_SRC}/converter/registry.cpp
	${BOOST_PYTHON_SRC}/str.cpp
	${BOOST_PYTHON_SRC}/tuple.cpp
	${BOOST_PYTHON_SRC}/converter/type_id.cpp
)

add_library(boost_python_modern STATIC ${BOOST_PYTHON_SOURCES})
target_include_directories(boost_python_modern PUBLIC
	"${BOOST_ROOT}/include"
	"${PYTHON24_ROOT}/include"
)
target_compile_definitions(boost_python_modern PRIVATE
	WIN32 NDEBUG _WINDOWS _MBCS BOOST_PYTHON_STATIC_LIB BOOST_PYTHON_SOURCE
)
target_compile_options(boost_python_modern PRIVATE /W3 /EHsc /GR /wd4996 /wd4244 /wd4267 /wd4305 /wd4503 /wd4786)
set_target_properties(boost_python_modern PROPERTIES
	OUTPUT_NAME "boost_python_modern_mt_1_32"
)

file(GLOB GAME_DLL_SOURCES CONFIGURE_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")
list(REMOVE_ITEM GAME_DLL_SOURCES "${CMAKE_CURRENT_SOURCE_DIR}/CvTextScreens.cpp")
add_library(CvGameCoreDLL SHARED ${GAME_DLL_SOURCES})
target_include_directories(CvGameCoreDLL PRIVATE
	"${BOOST_ROOT}/include"
	"${PYTHON24_ROOT}/include"
)
target_compile_definitions(CvGameCoreDLL PRIVATE
	WIN32 NDEBUG _WINDOWS _USRDLL CVGAMECOREDLL_EXPORTS FINAL_RELEASE BOOST_PYTHON_STATIC_LIB
	_SILENCE_STDEXT_HASH_DEPRECATION_WARNINGS
)
target_compile_options(CvGameCoreDLL PRIVATE
	/W3 /EHsc /GR /GS- /Gy /Oi /Ob2 /Oy /Zc:forScope- /wd4996 /wd4244 /wd4267
	/Zc:wchar_t- /wd4305 /wd4503 /wd4786 /wd4800 /wd4355 /wd4101 /wd4189
)
target_precompile_headers(CvGameCoreDLL PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}/CvGameCoreDLL.h")
target_link_libraries(CvGameCoreDLL PRIVATE
	boost_python_modern
	"${PYTHON24_ROOT}/libs/python24.lib"
	winmm
)
target_link_options(CvGameCoreDLL PRIVATE /MACHINE:X86 /LARGEADDRESSAWARE)
set_target_properties(CvGameCoreDLL PROPERTIES
	OUTPUT_NAME "CvGameCoreDLL"
	PREFIX ""
	SUFFIX ".dll"
)
