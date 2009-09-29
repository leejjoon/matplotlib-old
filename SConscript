import os
import sys

from numscons import GetNumpyEnvironment

from setupext import options

# This dict will be updated as we try to select the best option during
# the build process. However, values in setup.cfg will be used, if
# defined.
rc = {'backend':'Agg'}

AGG_VERSION = 'agg24'

env = GetNumpyEnvironment(ARGUMENTS)

def merge_build_dict(d1, d2):
    """Merge d2 'into' d1."""
    for k, v in d2.items():
        if v:
            d1[k].append(v)

    return d1

def CheckFreeType(context):
    # TODO
    #   - numscons.cfg customization (comes first)
    from numscons.checkers.config import _read_section
    from numscons.checkers.common import save_and_set, restore
    env = context.env

    context.Message("Checking for freetype2 ... ")

    src = r"""
#include <ft2build.h>

int main(void)
{
    return 0;
}
#if 0
%s
#endif
"""

    # Test using pkg-config
    pkg_config_name = None
    pkg_config_cmd = 'freetype-config'
    cmd_base = '!%s' % pkg_config_cmd

    if sys.platform == 'win32':
        raise NotImplementedError("Win32 support for pkg-config not implemented yet")
    else:
        cflags_cmd = [cmd_base]
        cflags_cmd.append('--cflags')
        compile_info = env.ParseFlags([' '.join(cflags_cmd)])

        link_cmd = [cmd_base]
        link_cmd.append('--libs')
        link_info = env.ParseFlags([' '.join(link_cmd)])

        build_info = merge_build_dict(compile_info, link_info)

        st = 0
        saved = save_and_set(env, build_info)
        try:
            st = context.TryLink(src % str(build_info), '.c')
        finally:
            restore(env, saved)

        if not st:
            context.Result('Failed (could not check header(s) : check config.log '\
        'in %s for more details)' % env['build_dir'])
            return st

    return context.Result('yes')

config = env.NumpyConfigure(custom_tests={'CheckFreeType': CheckFreeType})
#if not config.NumpyCheckLibAndHeader(libs='freetype',
#        headers='ft2build.h', section='freetype2'):
#    sys.exit(-1)
config.CheckFreeType()

has_libpng = True
if not config.NumpyCheckLibAndHeader(libs='png',
        headers='png.h', section='png'):
    has_libpng = False

config.Finish()

env.Append(CPPPATH=["%s/include" % AGG_VERSION, "."])
env.Append(CPPDEFINES={"PY_ARRAY_UNIQUE_SYMBOL": "MPL_ARRAY_API"})

common_cxx = [env.PythonObject(i) for i in env.Glob("CXX/*.cxx")]
env.NumpyPythonExtension("ft2font", source=common_cxx)

src = ['src/_ttconv.cpp', 'ttconv/pprdrv_tt.cpp', 'ttconv/pprdrv_tt2.cpp',
    'ttconv/ttutil.cpp']
env.NumpyPythonExtension("ttconv", source=src, CXXFILESUFFIX=".cpp")

env.NumpyPythonExtension("_cntr", source="src/cntr.c")

src = ["_delaunay.cpp", "VoronoiDiagramGenerator.cpp",
       "delaunay_utils.cpp", "natneighbors.cpp"]
src = [os.path.join('lib/matplotlib/delaunay',s) for s in src]
env.NumpyPythonExtension("_delaunay", source=src, CXXFILESUFFIX=".cpp")

src = "src/nxutils.c"
env.NumpyPythonExtension('nxutils', source=src)

agg = ['agg_curves.cpp', 'agg_bezier_arc.cpp', 'agg_trans_affine.cpp', 'agg_vcgen_stroke.cpp']

src = ['%s/src/%s' % (AGG_VERSION, name) for name in agg]
src.extend(env.Glob('CXX/*.c'))
src.extend(common_cxx)

src.extend(['src/agg_py_transforms.cpp',
            'src/path_cleanup.cpp',
            'src/_path.cpp'])
env.NumpyPythonExtension('_path', source=src, CXXFILESUFFIX=".cpp")

# Optional components
if has_libpng and options['build_agg']:
    print "---- Missing: build_agg ----"
    rc['backend'] = 'Agg'
else:
    rc['backend'] = 'SVG'

if has_libpng and options['build_image']:
    print "---- Missing: build_image ----"

if has_libpng and options['build_agg'] or options['build_image']:
    print "---- Missing: build_png ----"

if options['build_windowing'] and sys.platform=='win32':
    print "---- Missing: build_windowing ----"

