import MeCab
from scipy.misc import imread
from os import path
# import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
import numpy as np
from PIL import Image

d = path.dirname(__file__)
with open(path.join(d, 'kairozu.txt')) as f:
    kailines = f.readlines()
f.close()

mct = MeCab.Tagger("-O chasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd/")
kai_tokenized = ''

for sentence in kailines:
    jparse = mct.parseToNode(sentence)
    while jparse:
        #10: adjectives, 31: verbs, 36-47,49: nouns
        if jparse.posid in [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49]:
            mct_split = jparse.feature.split(',')
            if mct_split[6] != '*':
                kai_tokenized = kai_tokenized + mct_split[6] + ' '
        jparse = jparse.next

# I used a Google Noto font: https://www.google.com/get/noto/
font_path = d + '~/Library/Fonts/NotoSansCJKjp-Light.otf'

# orange version of Kai the Koi is used for both the word cloud colors
# and the shape of the wordcloud itself (the mask)
kai_coloring = imread(path.join(d, 'kaikoiorange.jpg'))
mask = np.array(Image.open(path.join(d, 'kaikoiorange.jpg')))
image_colors = ImageColorGenerator(kai_coloring)    # generate image colors

# Generate the word cloud itself, using the following options:
# collocations: whether to include collocations (bigrams) of two words
# mask: the shape of the word cloud -- taken from Kai the Koi above
# scale: scaling between computation and drawing, lower=faster, higher=better resolution
# relative_scaling: importance of relative word frequencies for font size
# color_func: use the colors generated above w/ImageColorGenerator
wordcloud = WordCloud(collocations=False, mask=mask, background_color="white", font_path=font_path, contour_width=1, max_words=4000, max_font_size=110, min_font_size=10, scale=4, relative_scaling=0.5, color_func=image_colors, random_state=3).generate(kai_tokenized)

# # matplotlib preview of wordcloud
# plt.figure()
# plt.imshow(wordcloud, interpolation="bilinear")
# plt.axis("off")
# plt.show()
#
# # image preview of wordcloud
# image = wordcloud.to_image()
# image.show()

# save wordcloud image
wordcloud.to_file(path.join(d, "kairozu_word_cloud.png"))