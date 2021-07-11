from typing import (
    Dict
)

from user import UnixUser


class JsonAttributeUser:
    name = "pw_name"
    password = "pw_passwd"
    uid = "pw_uid"
    gid = "pw_gid"
    gecos = "pw_gecos"
    dir = "pw_dir"
    shell = "pw_shell"


def _fmt_users(unix_user: UnixUser) -> Dict:
    return {
        JsonAttributeUser.name: unix_user.name,
        JsonAttributeUser.password: "x",
        JsonAttributeUser.uid: unix_user.uid,
        JsonAttributeUser.gid: unix_user.group.id,
        JsonAttributeUser.gecos: unix_user.gecos,
        JsonAttributeUser.dir: unix_user.home_dir,
        JsonAttributeUser.shell: unix_user.shell
    }


class JsonFormatterUser(dict):

    def __init__(self, unix_user: UnixUser):
        super().__init__(_fmt_users(unix_user))
