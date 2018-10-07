import MeCab
from os import path
from wordcloud import WordCloud, STOPWORDS

# (1) load the text file with the story
d = path.dirname(__file__)          # directory interface for file access
with open(path.join(d, 'momotaro.txt')) as f:
    momotaro = f.readlines()

# (2) tokenize the text
mct = MeCab.Tagger("-O chasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd/")
momo_text = ''
for sentence in momotaro:
    jparse = mct.parseToNode(sentence)
    while jparse:
        mct_split = jparse.feature.split(',')
        momo_text = momo_text + mct_split[6] + ' '  # keep dictionary form
        jparse = jparse.next

# (3) indicate words I don't want to include in the word cloud
stopwords = set(STOPWORDS)
stopwords.add("です")
stopwords.add("する")
stopwords.add("ます")

# (4) create the word cloud
font_path = d + '~/Library/Fonts/NotoSansCJKjp-Light.otf'
wordcloud = WordCloud(background_color="white", stopwords=stopwords, font_path=font_path).generate(momo_text)

image = wordcloud.to_image()
image.show()                    # display generated wordcloud

# # save wordcloud image
# wordcloud.to_file(path.join(d, "momo_word_cloud.png"))