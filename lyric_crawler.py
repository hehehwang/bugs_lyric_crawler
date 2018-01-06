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

### Initialize Golbal Variables
wc_mask_enable = False
wc_mask_filename = 'mask.png'

### Function Definition
def Timestamp():
    nnnn = time.localtime()
    tp = "%d%02d%02d_%02d%02d_%02d" % (
    nnnn.tm_year, nnnn.tm_mon, nnnn.tm_mday, nnnn.tm_hour, nnnn.tm_min, nnnn.tm_sec)
    return tp

def Output_csv_more_than(ll, n, suffix = ''):
    tp = Timestamp()
    output_file_csv = open('./output/data_out_' + tp + suffix +'.csv', 'w+', encoding='utf-8', newline='')

    wr_csv = csv.writer(output_file_csv)
    wr_csv.writerow(('Word','Quantity'))
    for idx in ll:
        if idx[1] > n:
            wr_csv.writerow(idx)
    output_file_csv.close()

def Output_wc(word_dic, suffix = ''):
    if wc_mask_enable:
        mask_ext = wc_mask_filename.split('.')[-1]
        maskk = np.array(Image.open('./mask/' + wc_mask_filename))
        maskk_color = ImageColorGenerator(maskk)
        wc = WordCloud(font_path='c:/Windows/Fonts/NanumMyeongjo.ttf',
                       background_color='white',
                       mask = maskk).generate_from_frequencies(word_dic)
        tp = Timestamp()
        wc.to_file('./output/data_out_' + tp + suffix + '_origin.' + mask_ext)
        wc.recolor(color_func=maskk_color)
        wc.to_file('./output/data_out_' + tp + suffix + '_colored.' + mask_ext)
    else:
        wc = WordCloud(font_path='c:/Windows/Fonts/malgun.ttf',
                       width=800,
                       height=400).generate_from_frequencies(word_dic)
        tp = Timestamp()
        wc.to_file('./output/data_out_' + tp + suffix +'.png')

def Str_to_bool(ss):
    if ss in ['T', 't']:
        return True
    else:
        return False
### End of Functions

### Initialize Default Variables
output_ko_only, output_csv, output_wc, output_txt = False, True, True, True
csv_min = 3
track_num_limit = None
### Importing Settings from setting.ini
"""
setting.ini configuration:
- Html Parsing config:
track_num_limit = [int]

- output config (csv, wordcloud, txt):
_output_csv = [bool]
_output_wc = [bool]
_output_txt = [bool]
_output_ko_only = [bool]

- csv config
csv_min = [int]

- Wordcloud config (mask, recolor, bgcolor,...)
wc_mask_enable
wc_mask_filename
_wc_mask_recolor
_wc_bgcolor
"""
print('Checking settings.ini...')
time.sleep(1)
with open('settings.ini', 'r', encoding='utf-8') as f:
    doc = f.readlines()
    for d in doc:
        d = d.strip()
        if d != '' and d[0] != '#':
            l = d.split('=')
            attr = l[0].strip()

            if attr == 'track_num_limit':
                if l[1].strip() == '0':
                    track_num_limit = None
                    print('All tracks on chart will be collected')
                else:
                    track_num_limit = int(l[1].strip())
                    print('Number of tracks to be collected: ' + str(track_num_limit))

            elif attr == 'output_ko_only':
                output_ko_only = Str_to_bool(l[1].strip())
            elif attr == 'output_csv':
                output_csv = Str_to_bool(l[1].strip())
            elif attr == 'output_wc':
                output_wc = Str_to_bool(l[1].strip())
            elif attr == 'output_txt':
                output_txt = Str_to_bool(l[1].strip())

            elif attr == 'wc_mask_enable':
                wc_mask_enable = Str_to_bool(l[1].strip())
                print('Use Mask Image: ' + str(wc_mask_enable))

            elif attr == 'wc_mask_filename':
                if l[1].strip().split('.')[-1] in ['jpg', 'jpeg', 'png']:
                    wc_mask_filename = l[1].strip()
                    print('Name of Mask Image file: ' + str(wc_mask_filename))
                else:
                    print('Inappropriate Mask Image Extension!')
                    time.sleep(3)
                    sys.exit()

            else:
                continue
        else:
            continue
print('...Done')
print('\n'+'='*40+'\n')

time.sleep(5)

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
if wc_mask_enable:
    if not os.path.exists('./mask/' + wc_mask_filename):
        print('WARNING: There is no mask File(or Directory)!\nShould I run without mask file? (Y/N)')
        reply = input()
        if reply == 'Y' or reply == 'y':
            wc_mask_enable = False
            print('...OK!')
        else:
            print('Goodbye!')
            time.sleep(3)
            sys.exit()
    else:
        print('Mask File - Checked\n')

print('\nAll is well!\n\n')

time.sleep(1)

### Scrapping
print('Now Scrapping Charts from Bugs.co.kr...')
## html scrap - 1. track list scrapping from bugs
html_chart = urlopen("https://music.bugs.co.kr/chart")
bsobj_chart = bs4.BeautifulSoup(html_chart, "html.parser")
chart_filtered = bsobj_chart.tbody.findAll("tr")
print('...Done\n')

track_num_list = []
track_name_list = []
for i in chart_filtered:
    try:
        track_num_list.append(i['trackid'])
    except:
        continue

## html scrap - 2. scrapping lyrics from bugs
lyrics = ''
track_num_list = track_num_list[:track_num_limit]
cnt = 1

print('Now Scrapping Lyrics from Bugs.co.kr...')
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
print('...Done\n')

### Analysing Lyrics
kk = Hannanum()

# dic for korean only
d_ko = Counter(kk.nouns(lyrics))
l_ko = sorted(d_ko.items(), key=itemgetter(1), reverse=True)

if output_csv: Output_csv_more_than(l_ko, csv_min, suffix='_ko')
if output_wc: Output_wc(d_ko, suffix='_ko')

if not output_ko_only:
    d_all = {}
    for s in kk.pos(lyrics):
        if s[1] == 'N' or s[1] == 'F':
            if s[0] not in d_all.keys():
                d_all[s[0]] = 1
            else:
                d_all[s[0]] += 1
    l_all = sorted(d_all.items(), key=itemgetter(1), reverse=True)
    if output_csv: Output_csv_more_than(l_all, csv_min, suffix='_all')
    if output_wc: Output_wc(d_all, suffix='_all')

if output_txt:
    print('OUTPUT: Writing lyric text files...')
    with open('./output/lyric_' + Timestamp() + '.txt', 'w', encoding='utf-8') as f:
        f.write(lyrics)
    print('...Done')

print('\nALL WORK IS DONE!')
_ = input()