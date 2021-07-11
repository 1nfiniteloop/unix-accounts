from typing import (
    Dict
)

from password import UnixPassword


class JsonAttributePassword:
    name = "sp_namp"
    password = "sp_pwdp"
    last_change = "sp_lstchg"
    days_min = "sp_min"
    days_max = "sp_max"
    days_warn = "sp_warn"
    days_inactive = "sp_inact"
    expire = "sp_expire"


def _fmt_passwords(unix_password: UnixPassword) -> Dict:
    return {
        JsonAttributePassword.name: unix_password.name,
        JsonAttributePassword.password: unix_password.encrypted_password,
        JsonAttributePassword.last_change: unix_password.days_since_epoch_last_change,
        JsonAttributePassword.days_min: unix_password.days_min,
        JsonAttributePassword.days_max: unix_password.days_max,
        JsonAttributePassword.days_warn: unix_password.days_warn,
        JsonAttributePassword.days_inactive: unix_password.days_inactive,
        JsonAttributePassword.expire: unix_password.days_since_epoch_expires,
    }


class JsonFormatterPassword(dict):

    def __init__(self, unix_password: UnixPassword):
        super().__init__(_fmt_passwords(unix_password))
