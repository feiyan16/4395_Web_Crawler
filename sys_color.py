class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def stdout(text):
    print(f"{Colors.OKBLUE}{text}{Colors.ENDC}")


def stdin(text):
    return input(f"{Colors.OKBLUE}{text}{Colors.ENDC}")


def stdok(text):
    print(f"{Colors.OKGREEN}{Colors.BOLD}{text}{Colors.ENDC}")


def stdwarn(text):
    print(f"{Colors.WARNING}\tWARNING: {text}...{Colors.ENDC}")


def stderr(text):
    print(f"{Colors.FAIL}{Colors.BOLD}ERROR: {text}!{Colors.ENDC}")