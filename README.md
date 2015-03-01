Taningia Shell
==============
A super-user shell which allow controlling multiple hosts in a smart way (Prototype)

**Features:**

* Easy to use interactive mode (default)
* Easy CLI wizard to save command-groups/host-groups
* Options to run commands/command-groups non-interactively (e.g compatible with crontab)

**Installation:**

`wget https://raw.githubusercontent.com/mahmoudadel2/taningia-shell/master/taningia-shell.py -O /usr/local/bin/taningia-shell`

`chmod +x /usr/local/bin/taningia-shell`

**How to use:**

Interactive mode (default):

* call the command plus the target host/hosts separated by comma:

`taningia-shell host1.example.com,host2.example.com`

* You can specify another user than your current user by entering the hosts that way:

`taningia-shell ubuntu@host1.example.com,root@host2.example.com`

* You can specify another port than port 22 by entering the hosts that way:

`taningia-shell host1.example.com:2222,ubuntu@host2.example.com:4422`

* Now you are attached to 2 hosts with 1 prompt, type the commands you need:

```
taningia-shell@2-hosts> hostname
Output from host1.example.com:
host1

Output from host2.example.com:
host2

```

* As long as you type commands the commands are recorded, if you want to save the commands you type as a command-group for easier call-back in the future:

`taningia-shell@2-hosts> save`

* To run a previously saved command-group:

`taningia-shell@2-hosts> run`

* You can use `save` for saving the hosts also as host-group.

* To connect to a previously saved host-group, pass the host-group instead of host/hosts argument when call taningia-shell command:

`taningia-shell host-group1`

Non-interactive mode:

* To run command on certain host/hosts/host-group:

`taningia-shell host1.example.com,host2.example.com -r hostname`

* To run a command-group on certain host/hosts/host-group:

`taningia-shell host1.example.com,host2.example.com -g command-group1`

**Configuration files:**

* /opt/taningia-shell/etc/commandgroups.cfg

* /opt/taningia-shell/etc/hostgroups.cfg

**Uninstallation:**

`rm -v /usr/local/bin/taningia-shell`

`rm -rvf /opt/taningia-shell/`