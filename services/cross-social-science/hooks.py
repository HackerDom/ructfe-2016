from sanic.log import log


def after_start(loop):
    log.info("OH OH OH OH OHHHHHHHH")


def before_stop(loop):
    log.info("TRIED EVERYTHING")
