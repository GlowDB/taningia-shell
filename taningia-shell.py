#!/usr/bin/env python
__author__ = 'Mahmoud Adel <mahmoud.adel2@gmail.com>'
__version__ = 0.1
__license__ = "The MIT License (MIT)"

import os
import argparse
import uuid
import ConfigParser
import fabric.api as fabric
import shutil
import hashlib

class termcolors:
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'

parser = argparse.ArgumentParser(prog='taningia-shell')
parser.add_argument('hosts', metavar='HOSTS', help='Target host/hosts')
rootgroup = parser.add_mutually_exclusive_group()
groupactions = rootgroup.add_mutually_exclusive_group()
groupactions.add_argument('-r' ,'--run', metavar='', help='Command/Commands to run on the provided hosts')
groupactions.add_argument('-g', '--command-group', metavar='', help='Command-group to run on the provided hosts')

taningiashelldir = '/tmp/taningia-shell'
taningiashelltmpdir = taningiashelldir + '/tmp/'
taningiashellvardir = taningiashelldir + '/var/'
args = vars(parser.parse_args())
hosts = args['hosts'].split(',')
sessionid = str(uuid.uuid4())[-6:]
commands = dict()
hostgroupscfg = taningiashelldir + '/etc/' + 'hostgroups.cfg'
commandgroupscfg = taningiashelldir + '/etc/' + 'commandgroups.cfg'

def firsttimeinit():
    if not os.path.exists(taningiashelldir):
        os.mkdir(taningiashelldir)
        for directory in ('/etc', '/tmp', '/var/'):
            os.mkdir(taningiashelldir + directory)
        open(hostgroupscfg, 'a').close()
        open(commandgroupscfg, 'a').close()

def editfile(editor, file):
    if len(hosts) > 1:
        hostsdict = dict()
        index = 1
        for host in hosts:
            hostsdict[index] = host
            index += 1
        print hostsdict
        print index
        for key in hostsdict.keys():
            print str(key) + ') ' + hostsdict[key]
        try:
            hostkey = int(raw_input('Please insert the host to perform the edit action: '))
            if hostkey in hostsdict.keys():
                host = hostsdict[hostkey]
                print host
            else:
                print 'Nothing to do!'
                return
        except:
            print 'Nothing to do!'
            return
    else:
        host = str(hosts)
    filename = taningiashelltmpdir + sessionid + '-%s' % file.replace('/', '-')
    fabric.env.host_string = host
    fabric.env.warn_only = True
    fabric.get(file, filename)
    os.system('%s %s' % (editor, filename))
    fabric.put(filename, file)
    filemd5sum = hashlib.md5(open(filename).read()).hexdigest()
    shutil.copy(filename, taningiashelltmpdir + '/' + filemd5sum)
    commands[len(commands) + 1] = (file, filemd5sum)

def savecmd(cmds):
    for key in cmds.keys():
        print str(key) + ') ' + str(cmds[key])
    unwantedcmd = raw_input('Please insert the number of command(s) to ignore separated by comma: ')
    commandgroupname = raw_input('Please insert a name for the command-group: ')
    if len(unwantedcmd) != 0:
        for unwanted in unwantedcmd.split(','):
            try:
                if int(unwanted) in cmds.keys():
                    cmds[int(unwanted)] = 'Unwanted'
            except:
                print 'Nothing to do!'
                return
    with open(commandgroupscfg, 'a') as f:
        f.writelines('[%s]\n' % commandgroupname)
        f.writelines('commands = \n')
        for cmd in cmds.values():
            if cmd == 'Unwanted':
                continue
            elif type(cmd) == tuple:
                f.writelines('  TSPUT:%s,%s\n' % cmd)
                shutil.copy(taningiashelltmpdir + '/' + cmd[1], taningiashellvardir + '/' + cmd[1])
            else:
                f.writelines('  %s\n' % cmd)

def savehosts(hosts):
    hostgroupname = raw_input('Please insert a name for the host-group: ')
    with open(hostgroupscfg, 'a') as f:
        f.writelines('[%s]\n' % hostgroupname)
        f.writelines('hosts = \n')
        for host in hosts:
            f.writelines('  %s\n' % host)

def checkconflicts():
    pass

def checkhostgroups():
    config = ConfigParser.RawConfigParser()
    config.read(hostgroupscfg)
    for host in hosts:
        if config.has_section(host):
            hosts.remove(host)
            for item in config.get(host, 'hosts').splitlines():
                if len(item) != 0: hosts.append(item)

def runcommandgroup(hosts):
    config = ConfigParser.RawConfigParser()
    config.read(commandgroupscfg)
    for section in config.sections():
        print section
    cmdgroup = raw_input('Please choose command group to run: ')
    if cmdgroup in config.sections():
        for host in hosts:
            fabric.env.warn_only = True
            fabric.env.host_string = host
            with fabric.hide('running', 'output'):
                for cmd in config.get(cmdgroup, 'commands').splitlines():
                    if len(cmd) != 0:
                        if 'TSPUT' in cmd:
                            filedata = str(cmd.split(':')[1]).split(',')
                            with fabric.show('running', 'output'):
                                fabric.put(taningiashellvardir + '/' + filedata[1], filedata[0])
                        else:
                            output = fabric.run(cmd)
                            print '''%sOutput from %s:%s
%s
''' % (termcolors.MAGENTA, host, termcolors.END, output)
    else:
        print 'Nothing to do!'

def connect(hosts):
    try:
        while True:
            cmd = raw_input('%staningia-shell@%s-hosts> %s' % (termcolors.GREEN, len(hosts), termcolors.END))
            if 'vim' in cmd or 'vi' in cmd or 'nano' in cmd:
                editor = cmd.split()[0]
                rfile = cmd.split()[len(cmd.split()) - 1]
                editfile(editor, rfile)
            elif cmd == 'run':
                runcommandgroup(hosts)
            elif cmd == 'save':
                choice = raw_input('What do want to save:\n1) Commands.\n2) Hosts.\nPlease insert your choice (1,2): ')
                if choice == '1':
                    savecmd(commands)
                elif choice == '2':
                    savehosts(hosts)
                else:
                    print 'Nothing to do!'
            else:
                if len(cmd) != 0:
                    commands[len(commands) + 1] = cmd
                    for host in hosts:
                        fabric.env.warn_only = True
                        fabric.env.host_string = host
                        with fabric.hide('running', 'output'): output = fabric.run(cmd)
                        print '''%sOutput from %s:%s
        %s
        ''' % (termcolors.MAGENTA, host, termcolors.END, output)
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass

def run(cmd, group=False):
    if group:
        config = ConfigParser.RawConfigParser()
        config.read(commandgroupscfg)
        cmdgroup = cmd
        if cmdgroup in config.sections():
            for host in hosts:
                fabric.env.warn_only = True
                fabric.env.host_string = host
                with fabric.hide('running', 'output'):
                    for cmd in config.get(cmdgroup, 'commands').splitlines():
                        if len(cmd) != 0:
                            output = fabric.run(cmd)
                            print '''%sOutput from %s:%s
%s
''' % (termcolors.MAGENTA, host, termcolors.END, output)
    else:
        for host in hosts:
            fabric.env.warn_only = True
            fabric.env.host_string = host
            with fabric.hide('running', 'output'): output = fabric.run(cmd)
            print '''%sOutput from %s:%s
%s
''' % (termcolors.MAGENTA, host, termcolors.END, output)

def main():
    firsttimeinit()
    checkhostgroups()
    if args['run'] != None:
        run(args['run'])
    elif args['command_group'] != None:
        run(args['command_group'], group=True)
    else:
        connect(hosts)

if __name__ == '__main__': main()