class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def colorize(text, color):
    return f"{color}{text}{bcolors.ENDC}"


class Ind:
    IND_SUCCESS = "OK"
    IND_FAIL = "NO"

    COL_SUCCESS = colorize(IND_SUCCESS, bcolors.OKBLUE)
    COL_FAIL = colorize(IND_FAIL, bcolors.FAIL)

    @staticmethod
    def mark(boolean=True):
        return Ind.COL_SUCCESS if boolean else Ind.COL_FAIL
