import logging
import sys
from datetime import datetime

from dockerlib import docker_run

logger = logging.getLogger("dockerize")
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s]%(levelname)s %(name)s: "
           "%(message)s at %(filename)s:%(lineno)d "
           "pid=%(process)d tid=%(thread)d")
OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
TARGET = 'python -u main.py'.split()
CHECK_ARGUMENTS = {
    1: lambda x: x in {'check', 'put', 'get'}
}


def sysclose(status=CHECKER_ERROR, public=""):
    if public:
        print("public: " + public)
    sys.exit(status)


def _check_args(argv):
    if len(argv) < 3:
        raise RuntimeError('Invalid arguments')
    for i, x in enumerate(argv):
        check = CHECK_ARGUMENTS.get(i, lambda x: True)
        if not check(x):
            raise RuntimeError('Invalid argument "{}" (index={})'.format(x, i))
    return argv[1], argv[2], argv[3:]


def main():
    argv = sys.argv[:]
    command, team_ip, argv = _check_args(argv)
    tid = team_ip.replace('.', '-')

    command = TARGET + [command, team_ip] + argv
    t1 = datetime.now()
    logger.info("start command inside docker: %r", command)
    r = (docker_run(tid, command, network='bridge'))
    t2 = datetime.now()
    logger.info("finish docker (%sms): status=%d",
                (t2 - t1).microseconds, r.returncode)
    sysclose(public=r.stdout)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except:
        _, e, _ = sys.exc_info()
        logger.exception(e)
        sysclose()
