# -*- coding: utf-8 -*-
"""
Bugs lyric crawler 1.0 by HeHeHwang
update: 2018.01.06
"""
import csv
import os
import time
from collections import Counter
from operator import itemgetter
from urllib.request import urlopen

import bs4
import numpy as np
from PIL import Image
from konlpy.tag import Hannanum
from wordcloud import WordCloud, ImageColorGenerator

### Golbal Variables
use_mask = False

### Function Definition
def timestamp():
    nnnn = time.localtime()
    tp = "%d%02d%02d_%02d%02d_%02d" % (
    nnnn.tm_year, nnnn.tm_mon, nnnn.tm_mday, nnnn.tm_hour, nnnn.tm_min, nnnn.tm_sec)
    return tp

def print_more_than(l, n):
    for idx in l:
        if idx[1] > n:
            print(idx)

def output_csv_more_than(l, n, suffix = ''):
    tp = timestamp()
    output_file_csv = open('./output/data_out_' + tp + suffix +'.csv', 'w+', encoding='utf-8', newline='')

    wr_csv = csv.writer(output_file_csv)
    wr_csv.writerow(('Word','Quantity'))
    for idx in l:
        if idx[1] > n:
            wr_csv.writerow(idx)
    output_file_csv.close()

def output_wordcloud(word_dic, suffix = ''):
    if use_mask:
        maskk = np.array(Image.open('./mask/mask.png'))
        maskk_color = ImageColorGenerator(maskk)
        wc = WordCloud(font_path='c:/Windows/Fonts/NanumMyeongjo.ttf',
                       background_color='lightgrey',
                       mask = maskk).generate_from_frequencies(word_dic)
        tp = timestamp()
        wc.to_file('./output/data_out_' + tp + suffix + '_origin' +'.png')
        wc.recolor(color_func=maskk_color)
        wc.to_file('./output/data_out_' + tp + suffix + '_colored' + '.png')
    else:
        wc = WordCloud(font_path='c:/Windows/Fonts/malgun.ttf',
                       width=800,
                       height=400).generate_from_frequencies(word_dic)
        tp = timestamp()
        wc.to_file('./output/data_out_' + tp + suffix +'.png')

### Directory & File check
if not os.path.exists('./output/'):
    os.mkdir('./output/')
if os.path.exists('./mask/mask.png'):
    use_mask = True

### Scrapping

## html scrap - 1. track list scrapping from bugs
html_chart = urlopen("https://music.bugs.co.kr/chart")
bsobj_chart = bs4.BeautifulSoup(html_chart, "html.parser")
chart_filtered = bsobj_chart.tbody.findAll("tr")

track_num_list = []
track_name_list = []
for i in chart_filtered:
    try:
        track_num_list.append(i['trackid'])
    except:
        continue

## html scrap - 2. scrapping lyrics from bugs
lyrics = ''

# limiting track numbers just for case
track_num_limit = 3
track_num_list = track_num_list[:track_num_limit]
cnt = 1

for trkid in track_num_list:
    html_track = urlopen("https://music.bugs.co.kr/track/"+trkid)
    bsobj_track = bs4.BeautifulSoup(html_track, "html.parser")
    track_filtered = bsobj_track.findAll("xmp")
    try:
        lyrics += track_filtered[0].get_text() + "\n"
    except:
        continue
    time.sleep(3)
    print("#"+str(cnt)+". " + trkid + " completed.")
    cnt += 1

print()

### Analysing Lyrics

# lyric parser (Ko)
kk = Hannanum()

# dic for en & korean
d_all = {}
# dic for korean only
d_ko = Counter(kk.nouns(lyrics))

for s in kk.pos(lyrics):
    if s[1] == 'N' or s[1] == 'F':
        if s[0] not in d_all.keys():
            d_all[s[0]] = 1
        else:
            d_all[s[0]] += 1
'''
    if s[1] == 'N':
        if s[0] not in d_ko.keys():
            d_ko[s[0]] = 1
        else:
            d_ko[s[0]] += 1
'''

l_all = sorted(d_all.items(), key=itemgetter(1), reverse=True)
output_csv_more_than(l_all, 3, suffix='_all')
output_wordcloud(d_all, suffix='_all')

l_ko = sorted(d_ko.items(), key=itemgetter(1), reverse=True)
output_csv_more_than(l_ko, 3, suffix='_ko')
output_wordcloud(d_ko, suffix='_ko')

with open('./output/lyric_' + timestamp() + '.txt', 'w', encoding='utf-8') as f:
    f.write(lyrics)

_ = input()