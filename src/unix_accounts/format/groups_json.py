from typing import (
    Dict
)

from group import UnixGroup


class JsonAttributeGroup:
    name = "gr_name"
    password = "gr_passwd"
    gid = "gr_gid"
    members = "gr_mem"


def _fmt_groups(unix_group: UnixGroup) -> Dict:
    return {
        JsonAttributeGroup.name: unix_group.name,
        JsonAttributeGroup.password: "x",
        JsonAttributeGroup.gid: unix_group.id,
        JsonAttributeGroup.members: unix_group.members
    }


class JsonFormatterGroup(dict):

    def __init__(self, unix_group: UnixGroup):
        super().__init__(_fmt_groups(unix_group))
