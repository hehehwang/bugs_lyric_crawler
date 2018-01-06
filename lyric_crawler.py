# -*- coding: utf-8 -*-
"""
Bugs lyric crawler 1.0a by HeHeHwang
update: 2018.01.06
"""
import csv
import os
import sys
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
mask_enable = False
mask_filename = ''
### Function Definition
def timestamp():
    nnnn = time.localtime()
    tp = "%d%02d%02d_%02d%02d_%02d" % (
    nnnn.tm_year, nnnn.tm_mon, nnnn.tm_mday, nnnn.tm_hour, nnnn.tm_min, nnnn.tm_sec)
    return tp

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
    if mask_enable:
        mask_ext = mask_filename.split('.')[-1]
        maskk = np.array(Image.open('./mask/' + mask_filename))
        maskk_color = ImageColorGenerator(maskk)
        wc = WordCloud(font_path='c:/Windows/Fonts/NanumMyeongjo.ttf',
                       background_color='white',
                       mask = maskk).generate_from_frequencies(word_dic)
        tp = timestamp()
        wc.to_file('./output/data_out_' + tp + suffix + '_origin.' + mask_ext)
        wc.recolor(color_func=maskk_color)
        wc.to_file('./output/data_out_' + tp + suffix + '_colored.' + mask_ext)
    else:
        wc = WordCloud(font_path='c:/Windows/Fonts/malgun.ttf',
                       width=800,
                       height=400).generate_from_frequencies(word_dic)
        tp = timestamp()
        wc.to_file('./output/data_out_' + tp + suffix +'.png')

### End of Functions

### Importing Settings from setting.ini
"""
setting.ini configuration:
track_num_limit
mask_enable
mask_filename
- wordcloud_bgcolor
- output_korean_only
"""
print('Checking settings.ini...')
time.sleep(1)
with open('settings.ini', 'r', encoding='utf-8') as f:
    doc = f.readlines()
    for d in doc:
        d = d.strip()
        l = d.split('=')
        if l[0].strip() == 'track_num_limit':
            track_num_limit = int(l[1].strip())
            print('Number of tracks to be collected: ' + str(track_num_limit))
        elif l[0].strip() == 'mask_enable':
            mask_enable = bool(l[1].strip())
            print('Use Mask Image or not: ' + str(mask_enable))
        elif l[0].strip() == 'mask_filename':
            if l[1].strip().split('.')[-1] in ['jpg', 'jpeg', 'png']:
                mask_filename = l[1].strip()
                print('Name of Mask Image file: ' + str(mask_filename))
            else:
                print('Inappropriate Mask Image Extension!')
                time.sleep(3)
                sys.exit()
        else:
            continue
print('...Done')
print('\n'+'='*40+'\n')

time.sleep(2)

### Directory & File check
print('Checking File and Directories')
if not os.path.exists('./output/'):
    print('Error: There is no output directory!')
    time.sleep(1)
    os.mkdir('./output/')
    print("...So I've made one JUST FOR YOU!!")
    time.sleep(1)
print('Output Directory - Checked\n')

print('Checking Mask Settings')
if mask_enable:
    if not os.path.exists('./mask/' + mask_filename):
        print('WARNING: There is no mask File(or Directory)!\nShould I run without mask file? (Y/N)')
        reply = input()
        if reply == 'Y' or reply == 'y':
            mask_enable = False
            print('...OK!')
        else:
            print('Goodbye!')
            time.sleep(3)
            sys.exit()
    else:
        print('Mask File - Checked\n')

print('..Done. \nAll is well!\n\n')

time.sleep(1)

print('Now Scrapping Informations from Bugs.co.kr...')
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

print('ALL WORK IS DONE!')
_ = input()