import random
from collections import deque
from collections import Counter
from collections import defaultdict
import functools

def shiftiter(iterable, n):
    '''Generator which yields iterable[0:n], iterable[1:n+1], ...

    Example: shiftiter(range(5), 3) yields (0, 1, 2), (1, 2, 3), (2, 3, 4)'''
    # I used deque, but I'm not sure it is fastest way:(
    it = iter(iterable)
    try:
        a = deque([next(it) for _ in range(n)])
        yield tuple(a)
    except StopIteration:
        pass
    for x in it:
        a.popleft()
        a.append(x)
        yield tuple(a)

def tee(func, arg):
    func(arg)
    return arg

def get_data():
    FILENAME = 'gcanna.ctd'
    FILEENCODING = 'eucjp'

    OUTNAME = 'out.txt'
    OUTENCODING = 'utf-8'

    USE_HIRAGANAS = ('あいうえおかきくけこさしすせそたちつてと' +
            'なにぬねのはひふへほまみむめもやゆよらりるれろわん' +
            'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ')

    hist = Counter()
    markov = defaultdict(Counter)

    try:
        with open(FILENAME, encoding=FILEENCODING) as f:
            for line in f:
                hiragana = line.split()[0]

                # 下のループに入れちまえって? まぁ、そうなんだけど。
                for x in hiragana:
                    if x in USE_HIRAGANAS:
                        hist[x] += 1

                for x,y in shiftiter(hiragana, 2):
                    if x in USE_HIRAGANAS and y in USE_HIRAGANAS:
                        markov[x][y] += 1
    # gcanna.ctdはアップロードしていないので、なければ代わりにout.txt読む。
    except IOError:
        ns = {}
        with open(OUTNAME, encoding=OUTENCODING) as f:
            for line in f:
                exec(line.replace("<class 'collections.Counter'>",
                                  'Counter'), globals(), ns)
            hist, markov = ns['hist'], ns['markov']
    # 後での確認用、もしくは、gcanna.ctdを持ってない人用に書き込んどく。
    else:
        with open(OUTNAME, 'w', encoding=OUTENCODING) as f:
            print('hist =', repr(hist), file=f)
            print('markov =', repr(markov), file=f)
    # 本当なら、markovは正規化して確率にした方がいい気がするが。
    # 整数のままの方が扱いやすい気もするので、とりあえずこのまま。
    return hist, markov


def make_text1(hist, height, width):
    '''ひらがなの出現頻度だけを考慮に入れて、ひらがなの羅列を作っても、
    単語らしきものはあまりできない、ということを示すための哀れな関数。'''
    n = sum(hist.values())
    keyvalues = hist.most_common()
    a = [keyvalues[0][1]]
    for x in keyvalues[1:]:
        a.append(a[-1] + x[1])

    def _get():
        x = random.randrange(n)
        for i,y in enumerate(a):
            if x < y:
                return keyvalues[i][0]

    return '\n'.join([''.join([_get() for _ in range(width)])
                     for _ in range(height)])

def make_text2(markov, hist, height, width):
    '''次にくるひらがなも考慮した、ひらがなの羅列。'''
    def _get(up, left):
        '''上の文字からの遷移と左の文字からの遷移を考える'''
        c = norm_markov[up] + norm_markov[left]
        x = random.random() * 2.0
        y = 0.0
        for k,v in c.most_common():
            y += v
            if x <= y:
                #print('_get:', up, left, '-->', k)
                return k

    # 上の文字、左の文字からの遷移を考えるので、0列目の前の列、0行目の前の行が
    # 必要になるが、便宜上、ひらがなの出現頻度から作った行を使用する。
    firstcol = make_text1(hist, 1, width)
    prevline = make_text1(hist, 1, width).strip()
    #print('firstcol', firstcol)
    #print('prevline', prevline)

    # markovを正規化する。
    # 上の文字からの遷移と左の文字からの遷移のウェイトを同じにするため。
    norm_markov = {}
    for k1,cnt in markov.items():
        c = Counter()
        n = sum(cnt.values())
        for k2,v in cnt.items():
            c[k2] = v / n
        norm_markov[k1] = c

    a = []
    for i in range(height):
        line = []
        functools.reduce(lambda x,j: tee(line.append, _get(prevline[j], x)),
                         range(width), firstcol[i])
        a.append(''.join(line))
        prevline = line
    return '\n'.join(a)

if __name__ == '__main__':
    hist, markov = get_data()
    print('ひらがなの出現頻度だけで、ひらがなの羅列')
    for i in range(1, 4):
        print(i, '回目')
        print(make_text1(hist, 16, 16))
        print()
    print('ひらがなの遷移を考慮した、ひらがなの羅列')
    for i in range(1, 4):
        print(i, '回目')
        print(make_text2(markov, hist, 16, 16))
        print()
