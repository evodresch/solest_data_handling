import sys
import time


def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█'):
    """
    Call in a loop to create a terminal progress bar.

    Parameters:
    iteration   - Required : current iteration (Int)
    total       - Required : total iterations (Int)
    prefix      - Optional : prefix string (Str)
    suffix      - Optional : suffix string (Str)
    decimals    - Optional : number of decimals in percentage (Int)
    length      - Optional : character length of bar (Int)
    fill        - Optional : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix)),
    # Print New Line on Complete
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()