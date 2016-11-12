import logging
import shlex
from collections import namedtuple
from subprocess import Popen, PIPE, run, STDOUT
import sys

log = logging.getLogger(__name__)

DockerResult = namedtuple('DockerResult', 'ok status is_timeout output name '
                                          'real_command command')
bin_docker = 'docker'
bin_timeout = 'timeout'
if sys.platform == 'darwin':
    bin_docker = '/usr/local/bin/docker'
if sys.platform == 'darwin':
    bin_timeout = '/usr/local/bin/gtimeout'


def kill_and_remove(ctr_name):
    for action in ('kill', 'rm'):
        p = Popen([bin_docker, action, ctr_name], stdout=PIPE, stderr=PIPE)
        if p.wait() != 0:
            log.info("kill_and_remove(): %r", repr(p.stderr.read()))
            # raise RuntimeError()


def inspect_container(name):
    cmd = [bin_docker, 'inspect',  '-f', '{{.State.Running}}', name]
    r = run(cmd, stderr=STDOUT, stdout=PIPE)
    has_container = r.returncode == 0
    is_running = b'false' not in r.stdout
    return has_container, is_running


def docker_exec(name, command, cwd=None):
    if cwd is None:
        cwd = '/'
    docker_command = [bin_docker, 'exec', '-it', name]
    if cwd != '/':
        docker_command += ['-w', cwd]

    docker_command += command
    return run(docker_command)


def docker_run(name, command, user="nobody", cwd=None, network='none',
               memory_limit='256m', image='pybasex', volumes=None, env=None,
               rm=True, daemon=False, hide=False):
    if volumes is not None and not isinstance(volumes, list):
        raise TypeError('volumes argument is not a list')
    if env is not None and not isinstance(env, dict):
        raise TypeError('env argument is not a dict')
    if memory_limit is not None:
        if not isinstance(memory_limit, str):
            raise TypeError('memory_limit argument is not a str')
        if not memory_limit or memory_limit[-1] not in 'bkmg':
            raise ValueError('memory_limit argument invalid (use '
                             '<number><unit> format, where unit can be one of '
                             'b, k, m, or g)')
    bin_docker = 'docker'
    bin_timeout = 'timeout'
    if sys.platform == 'darwin':
        bin_docker = '/usr/local/bin/docker'
    if sys.platform == 'darwin':
        bin_timeout = '/usr/local/bin/gtimeout'

    if cwd is None:
        cwd = '/'

    docker_command = [bin_docker, 'run', '--name', name]
    if daemon:
        docker_command += ['-d']
    if rm:
        docker_command += ['--rm']
    if network != 'bridge':
        docker_command += ['--net', network]
    if user != 'root':
        docker_command += ['-u', user]
    if cwd != '/':
        docker_command += ['-w', cwd]
    if volumes:
        for v in volumes:
            docker_command += ['-v', v]
    if env:
        for ek, ev in env.items():
            docker_command += ['-e', shlex.quote(str(ek) + '=' + str(ev))]

    if memory_limit:
        docker_command += ['-m', memory_limit]

    docker_command += [image] + command
    if hide:
        return run(docker_command, stdout=PIPE, stderr=PIPE)
    run(docker_command)


def docker_run_with_cache(uid, command, network='bridge', memory_limit=None):
    has_container, is_running = inspect_container(uid)
    if not has_container or not is_running:
        kill_and_remove(uid)
        docker_run(uid, ['/bin/sleep', '200000000'], network=network,
                   memory_limit=memory_limit, rm=False, daemon=True, hide=True)
    return docker_exec(uid, command)


def insecure_run(command):
    return run(command)
