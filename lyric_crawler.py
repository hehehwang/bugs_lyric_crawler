# -*- coding: utf-8 -*-
"""
Bugs lyric crawler 0.7 by HeHeHwang
update: 2018.01.07
"""
import configparser as cp
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
    # Variable Set-ups
    v = {}
    for items in ['wc_bgcolor', 'wc_mask_filename']:
        v[items] = cfg.get('Wordcloud', items)
    for items in ['wc_mask_origin', 'wc_mask_recolor']:
        v[items] = cfg.getboolean('Wordcloud', items)

    route = './output/data_out_' + Timestamp() + suffix

    if v['wc_mask_filename']:
        mask_ext = v['wc_mask_filename'].split('.')[-1]
        maskk = np.array(Image.open('./mask/' + v['wc_mask_filename']))
        maskk_color = ImageColorGenerator(maskk)
        wc = WordCloud(font_path='c:/Windows/Fonts/NanumMyeongjo.ttf',
                       min_font_size=6,
                       max_words=150,
                       background_color=v['wc_bgcolor'],
                       mask = maskk).generate_from_frequencies(word_dic)
        if v['wc_mask_origin']:
            wc.to_file(route + '_origin.' + mask_ext)
        if v['wc_mask_recolor']:
            wc.recolor(color_func=maskk_color)
            wc.to_file(route + '_colored.' + mask_ext)
    else:
        wc = WordCloud(font_path='c:/Windows/Fonts/malgun.ttf',
                       min_font_size=6,
                       background_color=v['wc_bgcolor'],
                       width=800,
                       height=400).generate_from_frequencies(word_dic)
        wc.to_file(route + '.png')


### End of Functions

### Importing Settings from setting.ini
"""
setting.ini configuration:
- Html Parsing config:
track_num_limit = [int]

- output config (csv, wordcloud, txt):
output_csv = [bool]
output_wc = [bool]
output_txt = [bool]
output_ko_only = [bool]

- csv config
csv_min = [int]

- Wordcloud config (mask, recolor, bgcolor,...)
wc_mask_enable
wc_mask_filename
wc_mask_recolor
wc_bgcolor
"""
print('Checking settings.ini...')
time.sleep(1)
cfg = cp.ConfigParser()
cfg.read('settings.ini')

track_num_limit = cfg.getint('Parsing', 'track_num_limit')
if track_num_limit == 0:
    track_num_limit = None

_ = 'Output Files'
output_ko_only= cfg.getboolean(_, 'output_ko_only')
output_csv = cfg.getboolean(_, 'output_csv')
output_wc = cfg.getboolean(_, 'output_wc')
output_txt = cfg.getboolean(_, 'output_txt')

csv_min = cfg.getint('csv','csv_min')

div = '\n'+'='*40+'\n'
# with open('settings.ini', 'r', encoding='utf-8') as f:
#     doc = f.readlines()
#     for d in doc:
#         d = d.strip()
#         if d != '' and d[0] != '#':
#             l = d.split('=')
#             attr = l[0].strip()
#
#             if attr == 'track_num_limit':
#                 if l[1].strip() == '0':
#                     track_num_limit = None
#                     print('All tracks on chart will be collected')
#                 else:
#                     track_num_limit = int(l[1].strip())
#                     print('Number of tracks to be collected: ' + str(track_num_limit))
#
#             elif attr == 'output_ko_only':
#                 output_ko_only = Str_to_bool(l[1].strip())
#             elif attr == 'output_csv':
#                 output_csv = Str_to_bool(l[1].strip())
#             elif attr == 'output_wc':
#                 output_wc = Str_to_bool(l[1].strip())
#             elif attr == 'output_txt':
#                 output_txt = Str_to_bool(l[1].strip())
#
#             elif attr == 'wc_bgcolor':
#                 wc_bgcolor = l[1].strip()
#             elif attr == 'wc_mask_enable':
#                 wc_mask_enable = Str_to_bool(l[1].strip())
#                 print('Use Mask Image: ' + str(wc_mask_enable))
#             elif attr == 'wc_mask_filename':
#                 if l[1].strip().split('.')[-1] in ['jpg', 'jpeg', 'png']:
#                     wc_mask_filename = l[1].strip()
#                     print('Name of Mask Image file: ' + str(wc_mask_filename))
#                 else:
#                     print('Inappropriate Mask Image Extension!')
#                     time.sleep(3)
#                     sys.exit()
#             elif attr == 'wc_mask_recolor':
#                 wc_mask_recolor = Str_to_bool(l[1].strip())
#
#             else:
#                 continue
#         else:
#             continue
print('...Done!')
print(div)

time.sleep(3)

### Directory & File check
print('Checking File and Directories')
if not os.path.exists('./output/'):
    print('ERROR?: There is no output directory!')
    time.sleep(1)
    os.mkdir('./output/')
    print("...So I've made one JUST FOR YOU!!")
    time.sleep(1)
print('Output Directory - Checked\n')

print('Checking Mask Settings')
maskfile = cfg.get('Wordcloud', 'wc_mask_filename')
if not maskfile:
    if not os.path.exists('./mask/' + maskfile):
        print('ERROR: There is no mask File(or Directory)!')
        time.sleep(3)
        sys.exit()
    elif maskfile.split('.')[-1] not in ['jpg', 'jpeg', 'png']:
        print('ERROR: Mask file extension does not match!')
        time.sleep(3)
        sys.exit()
    else:
        print('Mask File - Checked\n')
else:
    print('Not using Mask File - Checked')

print('\nAll is well!')
print(div)
time.sleep(1)

# <editor-fold desc="Scrapping part">
### Scrapping
print('Now Scrapping Charts from Bugs.co.kr...')
## html scrap - 1. track list scrapping from bugs
html_chart = urlopen("https://music.bugs.co.kr/chart")
bsobj_chart = bs4.BeautifulSoup(html_chart, "html.parser")
chart_filtered = bsobj_chart.tbody.findAll("tr")
print('...Done!\n')

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
print('...Done!')
print(div)
# </editor-fold>

### Analysing Lyrics
print('Now analysing lyrics... (ko)')
kk = Hannanum()

# dic for korean only
d_ko = Counter(kk.nouns(lyrics))
l_ko = sorted(d_ko.items(), key=itemgetter(1), reverse=True)
print('...Done!\n')
if output_csv:
    print('Now printing into .csv... (ko)')
    Output_csv_more_than(l_ko, csv_min, suffix='_ko')
    print('...Done!\n')
if output_wc:
    print('Now printing into Wordcloud... (ko)')
    Output_wc(d_ko, suffix='_ko')
    print('...Done!\n')

if not output_ko_only:
    print('Now analysing lyrics... (all)')
    d_all = {}
    for s in kk.pos(lyrics):
        if s[1] == 'N' or s[1] == 'F':
            if s[0] not in d_all.keys():
                d_all[s[0]] = 1
            else:
                d_all[s[0]] += 1
    l_all = sorted(d_all.items(), key=itemgetter(1), reverse=True)
    print('...Done!\n')
    if output_csv:
        print('Now printing into .csv... (all)')
        Output_csv_more_than(l_all, csv_min, suffix='_all')
        print('...Done!\n')
    if output_wc:
        print('Now printing into Wordcloud... (all)')
        Output_wc(d_all, suffix='_all')
        print('...Done!\n')

if output_txt:
    print('Now Writing lyric text files...')
    with open('./output/lyric_' + Timestamp() + '.txt', 'w', encoding='utf-8') as f:
        f.write(lyrics)
    print('...Done!\n')

print('\nJOB FINISHED!')
print(div)

_ = input()