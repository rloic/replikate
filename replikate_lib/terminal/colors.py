def info(s: str) -> str:
    return '\033[34m' + s + '\033[0m'


def log(s: str) -> str:
    return '\033[32m' + s + '\033[0m'


def warn(s: str) -> str:
    return '\033[33m' + s + '\033[0m'


def err(s: str) -> str:
    return '\033[31m' + s + '\033[0m'
