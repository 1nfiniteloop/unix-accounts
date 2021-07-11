# Unix-accounts

_Unix-accounts_ makes it possible to store accounts globally in one common
database, instead of manually keeping them synchronized locally on each
computers.

If having a shared network filesystem as example, the accounts (name, id) needs
to be synchronized between the computers. This does not scale well since the
effort to administrate accounts increases with the amount of computers times
the amount of accounts.

One solution is to to use ldap. However, the additional complexity to configure
the system and managing the accounts might not always balance up the gain. The
goal with this project has been to keep the account administration and system
configuration as simple and user-friendly as possible.

_Unix-accounts_ uses a sqlite-database* as storage backend and provides a
commandline interface to manage the accounts. It implements the nss api for
`passwd`, `group`, `shadow`. Simple and minimal, nothing more, nothing less.
The nss api is exposed over http(s) and is intended to be used with plugin
<https://github.com/1nfiniteloop/nss-http>.

*The storage backend can be switched to another sql-database, it is portable
and easy to replace since sqlalchemy is used.

__Note:__

This database is not intended to replace the regular account mechanism with
`/etc/{passwd,shadow,group}`. It extends the database lookups by using the name
service switch (nss) api. See more @
<http://man7.org/linux/man-pages/man5/nsswitch.conf.5.html>
and <https://www.gnu.org/software/libc/manual/html_node/NSS-Basics.html>.

The _Name Service Switch_ perform lookups only, example on
`getent {group,passwd,shadow}`. This means that changing account data is not
part of the nss api. Tools for changing accounts such as `passwd`, `useradd`,
`groupadd` is implemented to manipulate `/etc/{group,passwd,shadow}` directly.
Account administration is therefore done on the same computer as the
_unix-accounts_ server is on, using its provided commandline interface.

## Usage

### Install

Use docker-container (preferred), which starts the server as entrypoint:

        docker run -it \
          --name unix-accounts \
          --volume=unix-accounts:/var/opt/unix-accounts \
          --network=lan \
          1nfiniteloop/unix-accounts:latest

Or install with pip:

        pip install unix-accounts

### Server

__If installed with pip:__ Data is stored in `/var/opt/unix-accounts`. Create
this folder and give permissions accordingly, or provide alternative path with:
`--db=<path-to-sqlite-db> --token-db=<path-to-token-db>` on invocation.

Create a new token to give api access to passwords:

        unix-accounts-server --generate-token

Start server with:

        unix-accounts-server

Accounts can now be accessed with:

        curl -i \
            -H "Authorization: bearer MOE66ljNwXXF8R81OqGrDfbWmuZUjmlarDvdZt4X1dQ" \
            http://localhost:8025/api/{user,group,password}?name=foo

### Commandline interface

If installed with pip, access cli with:

        unix-accounts

If using docker-container, access cli with:

        docker exec -it unix-accounts unix-accounts

__General usage:__

        unix-accounts {group,user,group-member,password}

Use flag `--help` to see all options.

The commandline interface enters interactive mode if used without arguments.
This is more efficient since application loads the database once at start,
instead of on each command invocation.

Example: Add user

        unix-accounts# user add foo --uid 10000
        +-----------+-------+-------+-------+-----------+-----------+------------------+
        | User name | Id    | Group | Gecos | Home dir  | Shell     | Group membership |
        +-----------+-------+-------+-------+-----------+-----------+------------------+
        | foo       | 10000 | foo   |       | /home/foo | /bin/bash |                  |
        +-----------+-------+-------+-------+-----------+-----------+------------------+

Example: add user to a group

        unix-accounts# group-member add foo developer
        +------------+-------+-----------------+
        | Group name | Id    | User membership |
        +------------+-------+-----------------+
        | developer  | 10001 | foo             |
        +------------+-------+-----------------+

Example: set new password

        unix-accounts# password foo
        New password:

## Develop

### Run locally

Change to directory `unix-accounts/src`.

* Run unittests with `python3 -m unittest discover -s . -p "*_test.py"`.
* Start server with `python3 -m unix_accounts.bin.server [flags]`.
* Start interactive commandline interface with `python3 -m unix_accounts.bin.cli [flags]`.

### Build package

1. Make sure package build is available, or install with

        python3 -m pip install build

2. Build source and dist packages with:

        python3 -m build --wheel --sdist

3. The built wheel distribution is located in `dist/`, install with

        pip install dist/unix_accounts-1.0.0-py3-none-any.whl

### Build docker container

Note: The docker build uses the local built python package.

        docker build --tag 1nfiniteloop/unix-accounts:latest .
