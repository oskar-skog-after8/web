#!/usr/bin/ptyhon

# Copyright (c) Oskar Skog, 2016-2017
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# 1.  Redistributions of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
# 
# 2.  Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
# 
# This software is provided by the copyright holders and contributors "as is"
# and any express or implied warranties, including, but not limited to, the
# implied warranties of merchantability and fitness for a particular purpose
# are disclaimed. In no event shall the copyright holder or contributors be
# liable for any direct, indirect, incidental, special, exemplary, or
# consequential damages (including, but not limited to, procurement of
# substitute goods or services; loss of use, data, or profits; or business
# interruption) however caused and on any theory of liability, whether in
# contract, strict liability, or tort (including negligence or otherwise)
# arising in any way out of the use of this software, even if advised of the
# possibility of such damage.

import sys
import os

def myexit(code):
    '''
    Substitute for sys.exit.  MUST be used at EOF.
    
    This wrapper flushes output and calls `os._exit`.
    
    Python 2.7.10 on NetBSD 6.1 x86-32 has a bug that causes the
    interpreter to hang after the program has finished if it has ever
    called `subprocess.Popen`.  All of `exit`, `sys.exit`, `quit` and
    end of file are affected.
    
    Using `os._exit` won't work either because output is buffered and
    not flushed on exit.
    
    https://github.com/oskar-skog/anonymine/issues/7
    http://bugs.python.org/issue28807
    http://gnats.netbsd.org/cgi-bin/query-pr-single.pl?number=51657
    '''
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)


def expand(variable_name, all_variables, been_at=None):
    '''Do Makefile variable macro-expansion.
    
    `all_variables` is a dictionary of unexpanded Makefile variables,
    where `variable_name` is the key.
    
    `been_at` is a list of variable names to prevent infinite
    recursion.
    '''
    if been_at is None:
        been_at = [variable_name]
    else:
        if variable_name in been_at:
            raise ValueError('Infinite recursion of macro expansion detected.')
        else:
            been_at.append(variable_name)
    
    chunks = []
    var = all_variables[variable_name]
    while var:
        if '$' not in var:
            chunks.append(var)
            break
        # A dollar sign has been encountered.
        pre_dollar, post_dollar = var.split('$', 1)
        chunks.append(pre_dollar)
        if post_dollar[0] == '$':
            # Escaped dollar sign.
            chunks.append('$')
            var = post_dollar[1:]
            continue
        elif post_dollar[0] == '(':
            # Variable insertion.
            variable_name, post_variable = post_dollar[1:].split(')', 1)
            chunks.append(expand(variable_name, all_variables, been_at))
            var = post_variable
            continue
        else:
            raise ValueError('Unrecognised character after dollar sign.')
    return ''.join(chunks)


def getargs(flag_chars):
    '''Parse arguments.
    
    Makefile, flags = getargs(flag_chars)
    
    `flags_chars` is a string of short option (flag) characters.  The
    short options do not take any arguments.  Command line syntax:
        -F
    
    `Makefile` is a dictionary of the specified variables (long
    options) and some default variables.  The command line syntaxes are:
        key value
        key=value
        --key value
        --key=value
    
    `flags` is a dictionary where each character of `flag_chars` is a
    key. The value is True if the flag was specified and False if not.
    '''
    # Find all variables
    accept_flags = True
    flags = {}
    for c in flag_chars:
        flags[c] = False
    Makefile = {}
    try:
        while len(sys.argv) > 1:
            arg = sys.argv.pop(1)
            # Accept flags.
            if arg == '--':
                accept_flags = False
                continue
            if accept_flags:
                if arg[0] == '-' and arg[1] != '-':
                    for c in arg[1:]:
                        if c in flags:
                            flags[c] = True
                        else:
                            raise Exception('Bad flag: ' + c)
                    continue
            # * Having the value on the next argument is only allowed
            # with long options.
            # * We don't want leading dashes in the variable names.
            allow_separation = False
            if arg.startswith('--'):
                # --name[=value]
                arg = arg[2:]
                allow_separation = True
            if arg.startswith('-'):
                raise Exception('Only zero or two leading dashes are allowed.')
            # Check if the value is immediately assigned, or if it is
            # allowed to be assigned in the next
            if '=' in arg:
                # [--]name=value
                varname, value = arg.lstrip('-').split('=', 1)
                Makefile[varname] = value
            elif allow_separation:
                try:
                    value = sys.argv.pop(1)
                except IndexError:
                    raise Exception('Missing argument.')
                Makefile[arg] = value
            else:
                raise Exception('Missing argument.')
    except Exception:
        sys.stderr.write('Cannot parse your arguments.\n')
        sys.stderr.write('At "' + arg + '":\n')
        sys.stderr.write(str(sys.exc_info()[1]) + '\n')
        sys.stderr.write('There may be more errors.\n')
        myexit(1)
    
    return Makefile, flags


def check_variables(Makefile, flags):
    '''
    Check user specified variables. No infinite loops allowed, etc.
    
    Returns True if any variable has a bad value.  Otherwise False.
    '''
    error = False
    for variable in Makefile:
        # Name:
        for ch in variable:
            if ch in '$()':
                error = True
                sys.stderr.write(
                    'Variable name "' + variable + '" contains '
                    'a forbidden character. "$()"\n'
                )
                break
        # Value:
        try:
            for ch in expand(variable, Makefile):
                if ch in '"\'':
                    error = True
                    sys.stderr.write(
                        'Variable "' + variable + '" contains a quote.\n'
                    )
                    break
        except ValueError:
            # Infinite loops or incorrect syntax for variable expansion:
            error = True
            msg = str(sys.exc_info()[1])
            sys.stderr.write('Error in variable "'+variable+'": '+msg+'\n')
    # Check $USERPROFILE on Cygwin:
    for ch in os.getenv('USERPROFILE', ''):
        if ch in '"\'':
            error = True
            sys.stderr.write('There is a quote in %USERPROFILE%.\n')
            break
    if error:
        sys.stderr.write(
            './configure && make && make install may crash at any moment!\n'
        )
    return error


def chk_deps():
    ''' Check dependencies.  Return True if there was an error '''
    error = False
    try:
        import curses
    except:
        error = True
        sys.stderr.write(
            'Cannot import "curses" which is required by the game.\n'
        )
    try:
        import argparse
    except:
        # Not an error.
        sys.stderr.write('Cannot import "argparse". (Not required.)\n')
    major, minor = sys.version_info[:2]
    if major > 3:
        # Is this an error?
        sys.stderr.write('Python 3.x is the highest version I know of.\n')
    if major < 2 or (major == 2 and minor < 6):
        error = True
        sys.stderr.write('Python 2.6 or newer required. (Works with 3.x.)\n')
    return error


def find_prefix(Makefile, flags):
    '''
    All functions beginning with "find_" are Makefile variable generator
    function.
    It takes two arguments: Makefile and flags.
    
    `Makefile` is a dictionary of all Makefile variables to be prepended
    to the Makefile.
    
    `flags` is a dictionary where each key is a flag and its value is a
    boolean representing if the flag was set or not.
    
    Set Makefile['prefix'] if needed to.
    This is probably the first variable that needs to be set.
    '''
    # http://stackoverflow.com/questions/4271494/what-sets-up-sys-path-with-python-and-when
    if 'prefix' not in Makefile:
        trywith = [
            '/usr/local',
            '/usr/pkg',         # For Minix, MUST be above /usr
            '/usr',
            sys.prefix,         # '/usr/pkg' on Minix.
        ]
        for path in trywith:
            try:
                os.stat(path)
                if '/Library/Python/' not in ''.join(sys.path):
                    # Prevent this test from ever being used on a Mac.
                    assert path in ''.join(sys.path)  # Ugly but should work.
                assert path in os.getenv('PATH')  # Ugly but should work.
            except:
                continue
            Makefile['prefix'] = path
            return False
        else:
            sys.stderr.write('Cannot find $(prefix).\n')
            return True
    return False


def find_EXECUTABLES(Makefile, flags):
    '''
    See the doc-string for find_prefix as well.
    
    Set Makefile['EXECUTABLES'] if needed to.
    Depends (directly) on $(gamesdir) and $(bindir).
    Depends (indirectly) on $(prefix).
    '''
    if 'EXECUTABLES' not in Makefile:
        acceptable = os.getenv('PATH').split(':')
        for exec_dir in ('gamesdir', 'bindir'):
            if expand(exec_dir, Makefile) in acceptable:
                Makefile['EXECUTABLES'] = '$('+exec_dir+')'
                return False
        else:
            return True
    else:
        return False


def find_sysconfdir(Makefile, flags):
    '''
    See the doc-string for find_prefix as well.
    
    Set Makefile['sysconfdir'] if needed to.
    Depends on $(prefix)
    '''
    if 'sysconfdir' in Makefile:
        return False
    else:
        try:
            os.listdir(expand('prefix', Makefile) + '/etc')
            Makefile['sysconfdir'] = '$(prefix)/etc'
            return False
        except:
            pass
        Makefile['sysconfdir'] = '/etc'
        return False


def find_vargamesdir(Makefile, flags):
    '''
    See the doc-string for find_prefix as well.
    
    Set Makefile['localstatedir'] if needed to.
    Set Makefile['vargamesdir'] if needed to.
    Depends on $(prefix).
    '''
    if 'localstatedir' not in Makefile:
        try:
            os.listdir(expand('prefix', Makefile) + '/var')
            Makefile['localstatedir'] = '$(prefix)/var'
        except:
            try:
                os.listdir('/var')
                Makefile['localstatedir'] = '/var'
            except:
                return True
    if 'vargamesdir' not in Makefile:
        for tail in ('/games', ''):
            try:
                os.listdir(expand('localstatedir', Makefile) + tail)
                Makefile['vargamesdir'] = '$(localstatedir)' + tail
                return False
            except:
                pass
        else:
            return True
    else:
        return False


def find_MODULES(Makefile, flags):
    '''
    See the doc-string for find_prefix as well.
    
    Set Makefile['MODULES'] if needed to.
    Depends (directly) on $(libdir).
    Depends (indirectly) on $(prefix).
    
    $(MODULES) is where Python modules should be installed.
    '''
    if 'MODULES' in Makefile:
        return False
    
    libdir = expand('libdir', Makefile)
    prefix = expand('prefix', Makefile)
    prefixes = [libdir + '/python']
    try:
        import platform
        prefixes.append(libdir+'/'+platform.python_implementation().lower())
        prefixes.append(libdir+'/'+platform.python_implementation())
        prefixes.append(prefix+'/'+platform.python_implementation().lower())
        prefixes.append(prefix+'/'+platform.python_implementation())
    except ImportError:
        pass
    except AttributeError:
        pass
    suffixes = ['/site-packages', '/dist-packages']
    
    for suffix in suffixes:
        for prefix in prefixes:
            paths = list(filter(
                lambda path: path.startswith(prefix) and path.endswith(suffix),
                sys.path
            ))
            paths.sort(key=lambda s: len(s))
            if paths:
                # NOTICE:  Just notice this rather ugly construction.
                # You can't just change the data.
                if paths[0].startswith(libdir):
                    Makefile['MODULES'] = '$(libdir)' + paths[0][len(libdir):]
                else:
                    # prefix has been redefined, reredefine it
                    prefix = expand('prefix', Makefile)
                    Makefile['MODULES'] = '$(prefix)' + paths[0][len(prefix):]
                return False
    
    # Mac OS X
    # http://stackoverflow.com/questions/4271494/what-sets-up-sys-path-with-python-and-when
    # http://jessenoller.com/blog/2009/03/16/so-you-want-to-use-python-on-the-mac
    # http://stackoverflow.com/questions/13355370/what-is-the-difference-between-library-frameworks-python-framework-versions-2
    import re
    module_dirs_outside = [
        # pre-installed python:
        '^/Library/Python/[0-9.]+/site-packages$',
        # python.org
        '^/Library/Frameworks/Python.framework/Versions/[0-9.]+/lib/python[0-9.]+/site-packages/?$',
    ]
    for module_dir in module_dirs_outside:
        paths = list(filter(
            lambda path: re.match(module_dir, path) is not None, sys.path
        ))
        paths.sort(key=lambda s: len(s))
        if paths:
            Makefile['MODULES'] = paths[0]
            return False
    
    sys.stderr.write("Can't find directory for Python modules\n")
    return True


def find_INSTALL(Makefile, flags):
    '''
    See the doc-string for find_prefix as well.
    
    Sets Makefile['INSTALL'] if needed.
    
    $(INSTALL) is normally "install", but on Solares it needs to be
    "/usr/ucb/install".
    '''
    if 'INSTALL' not in Makefile:
        trywith = [
            '/usr/ucb/install'
        ]
        for install in trywith:
            try:
                os.stat(install)
            except:
                continue
            if flags['v']:
                sys.stdout.write('Using "' + install + '" as `install`\n.')
            Makefile['INSTALL'] = install
            return False
        Makefile['INSTALL'] = 'install'
        return False


def detect_desktop(Makefile, flags):
    '''
    See the doc-string for find_prefix as well.
    
    Sets Makefile['freedesktop'] if needed.
    Sets Makefile['macosx'] if needed.
    
    The value for these variables are either 'true' or 'false'.
    
    Checks for the existence of various desktop environments.
    '''
    # LOL, all these tests are based on listing a directory.
    mapping = {
        'freedesktop': '/usr/share/applications',
        'macosx': '/Applications',
    }
    for desktop in mapping:
        if desktop not in Makefile:
            try:
                os.listdir(mapping[desktop])
                Makefile[desktop] = 'true'
            except OSError:
                Makefile[desktop] = 'false'
    return False


def main():
    '''
    Parse arguments
    Generate Makefile variables
    Print messages in verbose mode
    Prepend Makefile variables to the output Makefile
    
    NOTICE:
    The defaults for $(srcdir), $(builddir), $(gamesdir), $(bindir) and
    $(libdir) are set in `getargs`.
    '''
    def v(s):
        if flags['v']:
            sys.stdout.write(s + '\n')
    
    # NOTICE: `getargs` pops items from sys.argv
    reconfigure_argv = sys.argv[1:]
    
    Makefile = {
        'srcdir': '',           # REQUIRED
        'builddir': '',         # REQUIRED
        'python': sys.executable,
        'gamesdir': '$(prefix)/games',
        'bindir': '$(prefix)/bin',
        'libdir': '$(prefix)/lib',
    }
    forced_vars, flags = getargs('fv')
    Makefile.update(forced_vars)
    
    error = chk_deps()
    # Find the prefix and check sanity of the variables.
    error |= find_prefix(Makefile, flags)
    error |= check_variables(Makefile, flags)
    # Fix builddir and srcdir
    Makefile['builddir'] = os.path.abspath(expand('builddir', Makefile)) + '/'
    Makefile['srcdir'] = os.path.abspath(expand('srcdir', Makefile)) + '/'
    # Find directories
    error |= find_EXECUTABLES(Makefile, flags)
    error |= find_MODULES(Makefile, flags)
    error |= find_sysconfdir(Makefile, flags)
    error |= find_vargamesdir(Makefile, flags)
    # and the install tool.
    error |= find_INSTALL(Makefile, flags)
    #
    error |= detect_desktop(Makefile, flags)
    
    if flags['v']:
        Makefile['verbose'] = 'true'
    else:
        Makefile['verbose'] = 'false'
    
    v('')
    if flags['v']:
        of_interest = (
            'prefix',
            'python',
            'EXECUTABLES',
            'MODULES',
            'INSTALL',
            'freedesktop',
            'macosx',
            'sysconfdir',
            'vargamesdir',
        )
        for variable in of_interest:
            try:
                sys.stdout.write(variable+' = '+Makefile[variable]+'\n')
                sys.stdout.write('(expand) "'+expand(variable, Makefile)+'"\n')
                sys.stdout.write('\n')
            except KeyError:
                sys.stderr.write('Missing variable: "'+variable+'"\n')
    
    # Don't write the Makefile if errors have occurred.
    if error:
        if flags['f']:
            sys.stderr.write(
                "There were errors, but you don't seem to care.\n")
        else:
            sys.stderr.write(
                'There were errors; no Makefile will be written.\n')
            myexit(1)
    
    # Write Makefile.
    
    inname = Makefile['srcdir'] + 'Makefile.static'
    Makefile_name = Makefile['builddir'] + 'Makefile'
    Makefile_vars_name = Makefile['builddir'] + 'Makefile.vars'
    v('Writing "' + Makefile_vars_name + '"...')
    v('Writing "' + Makefile_name + '" from "' + inname + '"...')
    
    Makefile_f = open(Makefile_name, 'w')
    Makefile_vars_f = open(Makefile_vars_name, 'w')
    for variable in sorted(Makefile):
        Makefile_f.write(variable + ' = ' + Makefile[variable] + '\n')
        Makefile_vars_f.write(variable + ' = ' + Makefile[variable] + '\n')
    Makefile_vars_f.close()
    
    inf = open(inname)
    Makefile_f.write(inf.read())
    Makefile_f.close()
    inf.close()
    
    # Write reconfigure.
    
    def shellescape(s):
        '''
        """foo""" -> """'foo'"""
        """foo'bar""" -> """'foo'"'"'bar"""
        """foo bar""" -> ""'foo bar'"""
        '''
        return "'" + s.replace("'", "\'\"\'\"\'") + "'"
    
    reconfigure_name = Makefile['builddir'] + 'reconfigure'
    v('Writing "' + reconfigure_name + '"...')
    reconfigure_f = open(reconfigure_name, 'w')
    
    reconfigure_f.write('#!/bin/sh\ncd {0} && {1} configure.py'.format(
        shellescape(Makefile['srcdir']),
        shellescape(sys.executable)
    ))
    for arg in reconfigure_argv:
        reconfigure_f.write(' ' + shellescape(arg))
    reconfigure_f.write('\n')
    
    reconfigure_f.close()
    os.system('chmod +x ' + shellescape(reconfigure_name))
    


if __name__ == '__main__':
    main()
    myexit(0)
