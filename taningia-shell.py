#!/usr/bin/env python
__author__ = 'Mahmoud Adel <mahmoud.adel2@gmail.com>'
__version__ = 0.1
__license__ = "The MIT License (MIT)"

import os
import argparse
import uuid
import fabric.api as fabric

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

taningiashelldir = '/tmp/taningia-shell'
args = vars(parser.parse_args())
hosts = args['hosts'].split(',')
sessionid = str(uuid.uuid4())[-6:]
commands = dict()

def firsttimeinit():
    if not os.path.exists(taningiashelldir):
        os.mkdir(taningiashelldir)
        for directory in ('/etc', '/tmp'):
            os.mkdir(taningiashelldir + directory)

def connect(hosts):
    try:
        while True:
            cmd = raw_input('%staningia-shell@%s-hosts> %s' % (termcolors.GREEN, len(hosts), termcolors.END))
            if 'vim' in cmd or 'vi' in cmd or 'nano' in cmd:
                print 'Editing command will be executed ' + cmd
            elif 'save commands' in cmd:
                print commands
                unwantedcmd = raw_input('Please insert the number of command(s) to ignore separated by comma: ')
                if len(unwantedcmd) != 0:
                    for unwanted in unwantedcmd.split(','):
                        if int(unwanted) in commands.keys():
                            commands[int(unwanted)] = 'Unwanted'
                with open(taningiashelldir + '/' + sessionid + '-commands.lst', 'w') as f:
                    for line in commands.values():
                        if 'Unwanted' in line:
                            continue
                        else:
                            f.writelines(line + '\n')
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

def run(cmd):
    if 'vim' in cmd or 'vi' in cmd or 'nano' in cmd:
        print 'Editing command will be executed ' + cmd
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
    if args['run'] != None:
        run(args['run'])
    else:
        connect(hosts)

if __name__ == '__main__': main()