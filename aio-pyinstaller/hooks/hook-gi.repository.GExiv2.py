# -*- coding: utf-8 -*-
#
# PyInstaller hook for gi.repository.GExiv2
#
# Collects the GExiv2 typelib and associated DLLs so that
# gi.require_version('GExiv2', '0.10') works in the frozen bundle.

from PyInstaller.utils.hooks.gi import GiModuleInfo

module_info = GiModuleInfo('GExiv2', '0.10')
if module_info.available:
    binaries, datas, hiddenimports = module_info.collect_typelib_data()
