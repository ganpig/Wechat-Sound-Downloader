from html.parser import HTMLParser
from urllib.request import urlopen

import easygui
from tqdm import tqdm


def urlget(url, tries=3):
    if tries:
        try:
            return urlopen(url, timeout=3).read().decode('utf-8')
        except:
            return urlget(url, tries - 1)
    else:
        return ''


mainUrls = easygui.textbox('请输入微信文章网址，每行一个', '微信音频下载器')

if mainUrls:
    for no, mainUrl in enumerate(mainUrls.splitlines()):
        data = urlget(mainUrl)

        class MainParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.data = []
                self.name = ''
                self.readFlag = 0

            def handle_starttag(self, tag, attrs) -> None:
                attrs = dict(attrs)
                if tag == 'a' and 'href' in attrs and (attrs['href'].startswith('https://mp.weixin.qq.com/s') or attrs['href'].startswith('http://mp.weixin.qq.com/s')):
                    self.data.append(attrs['href'])
                elif tag == 'meta' and 'property' in attrs and attrs['property'] == 'og:title':
                    self.name = attrs['content']

        mainParser = MainParser()
        mainParser.feed(data)
        filename = mainParser.name
        print(f'{no+1}/{len(mainUrls.splitlines())}', filename)
        result = []
        for url in tqdm(mainParser.data):
            data = urlget(url)

            class EachParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.data = ''
                    self.name = ''

                def handle_starttag(self, tag, attrs) -> None:
                    if tag == 'mpvoice':
                        self.data = dict(attrs)['voice_encode_fileid']
                        self.name = dict(attrs)['name']
            eachParser = EachParser()
            eachParser.feed(data)
            result.append(
                ('https://res.wx.qq.com/voice/getvoice?mediaid='+eachParser.data, eachParser.name))

        with open(filename+'.txt', 'w', encoding='utf-8') as f:
            for i, j in result:
                if all((i, j)):
                    print(i, file=f)
                    print(f' out={j}.mp3', file=f)
