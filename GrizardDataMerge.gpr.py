# Gramps registration file for the Grizard Data Merge tool.

from gramps.gen.plug._pluginreg import (
    TOOL,
    TOOL_DBPROC,
    TOOL_MODE_GUI,
    EXPERIMENTAL,
    EXPERT,
)
from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.version import major_version, VERSION_TUPLE

_ = glocale.translation.gettext

if (5, 2, 0) <= VERSION_TUPLE <= (6, 2, 0):
    register(
        TOOL,
        id="grizardmerge",
        name=_("Grizard Data Merge"),
        description=_(
            "Family Tree Processing Tool to compare another genealogy file "
            "(GEDCOM, Gramps XML, ...) side-by-side with the open Family Tree "
            "and merge selected differences person by person."
        ),
        version="0.1.1",
        gramps_target_version=major_version,
        status=EXPERIMENTAL,
        audience=EXPERT,
        fname="grizardmerge.py",
        authors=["Brian Caudill"],
        authors_email=["brian@bocaudill.com"],
        category=TOOL_DBPROC,
        toolclass="GrizardMergeTool",
        optionclass="GrizardMergeToolOptions",
        tool_modes=[TOOL_MODE_GUI],
        help_url=("https://gramps.discourse.group/t/10027"),
        # help_url=("Addon:Grizard_Merge_tool"),
    )
