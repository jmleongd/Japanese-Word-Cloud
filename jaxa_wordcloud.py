import tweepy
import re
import MeCab
import random
import numpy as np
from PIL import Image
from os import path
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# consumer keys and access tokens, used for OAuth -- you need to create these
# from your own Twitter account: https://apps.twitter.com/
consumer_key = 'YOUR_CONSUMER_KEY'
consumer_secret = 'YOUR_CONSUMER_SECRET'
access_token = 'YOUR_ACCESS_TOKEN'
access_token_secret = 'YOUR_ACCESS_TOKEN_SECRET'

# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)  # creation of the actual interface

d = path.dirname(__file__)  # directory interface for future files
jaxatweets = []             # raw @jaxa_jp tweets
jaxatweets_clean = []       # remove @YouTube references and hyperlinks
count = 0                   # count number of tweets downloaded

# tweet_mode='extended' pulls the full text of a tweet (the default is truncated after 140)
for status in tweepy.Cursor(api.user_timeline, screen_name='@jaxa_jp', tweet_mode='extended').items():
    if (not status.retweeted) and ('RT @' not in status._json['full_text']):    # remove retweets
        cleantweet = re.sub(r'https://t.co/[a-zA-Z0-9]{10}', '', status._json['full_text'])
        cleantweet = re.sub(r'、@YouTube がアップロード', '', cleantweet)
        cleantweet = re.sub(r'@YouTube', '', cleantweet)
        jaxatweets.append(status._json['full_text'])        # save raw tweets
        jaxatweets_clean.append(cleantweet)                 # save clean tweets
        count = count+1

print("# of Tweets Saved: " + str(count))

# save backup of raw tweets
savetweets = open("jaxa_tweets.txt", "w")
for tweet in jaxatweets:
    savetweets.write(tweet + "\n")
savetweets.close()

# save backup of regex cleaned tweets
savetweets_clean = open("jaxa_tweets_clean.txt", "w")
for tweet in jaxatweets_clean:
    savetweets_clean.write(tweet + "\n")
savetweets_clean.close()

# # load the previously saved tweets
# with open(path.join(d, 'jaxa_tweets_clean.txt')) as f:
#     jaxatweets_clean = f.readlines()

mct = MeCab.Tagger("-O chasen -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd/")
sentence_analysis = open("jaxa_tweets_words_all.txt", "w")
jaxa_text_full = ''

# use MeCab to tokenize sentences (keep adjectives, verbs, and nouns)
for sentence in jaxatweets_clean:
    jaxa_text = ''
    jparse = mct.parseToNode(sentence)
    while jparse:
        # 10: adjectives, 31: verbs, 36-47,49: nouns
        if jparse.posid in [10, 31, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49]:
            mct_split = jparse.feature.split(',')
            if mct_split[6] != '*':
                if re.search(r'[a-zA-Z]', mct_split[6]):
                    jaxa_text = jaxa_text + jparse.surface + ' '    # keep word-in-place
                else:
                    jaxa_text = jaxa_text + mct_split[6] + ' '      # keep dictionary form
        jparse = jparse.next
    sentence_analysis.write(jaxa_text)
    jaxa_text_full = jaxa_text_full + ' ' + jaxa_text
sentence_analysis.close()

# word-cloud color range; JAXA Blue taken from logo SVG: HSL 207 100% 35%
def jaxa_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(207, 100%%, %d%%)" % random.randint(20, 65)

# # load the previously saved text
# jaxa_text = open(path.join(d, 'jaxa_tweets_words_all.txt')).read()

# I used a Google Noto font: https://www.google.com/get/noto/
font_path = d + '~/Library/Fonts/NotoSansCJKjp-Light.otf'

# jpg created from JAXA logo SVG on Wikipedia
# https://commons.wikimedia.org/wiki/File:Jaxa_logo.svg
mask = np.array(Image.open(path.join(d, "jaxa_logo_large.jpg")))

# Generate the word cloud itself, using the following options:
# collocations: whether to include collocations (bigrams) of two words
# font_path: font path to the font that will be used (OTF or TTF)
# mask: the shape of the word cloud -- taken from JAXA logo above
# scale: scaling between computation and drawing, lower is faster
# relative_scaling: importance of relative word frequencies for font-size
# color_func: returns a PIL color for each word
wordcloud = WordCloud(collocations=False, mask=mask, background_color="white", font_path=font_path, max_words=4000, max_font_size=110, min_font_size=8, scale=4, relative_scaling=0.3, color_func=jaxa_color_func, random_state=3).generate(jaxa_text_full)

# matplotlib preview of wordcloud
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()

# image preview of wordcloud
image = wordcloud.to_image()
image.show()

# save wordcloud image w/o highlights
wordcloud.to_file(path.join(d, "jaxa_word_cloud.png"))

# create additional version with red highlight for defined words (aka words I liked)
class SimpleGroupedColorFunc(object):
    def __init__(self, color_to_words, default_color):
        self.word_to_color = {word: color
                              for (color, words) in color_to_words.items()
                              for word in words}
        self.default_color = default_color

    def __call__(self, word, **kwargs):
        return self.word_to_color.get(word, self.default_color)

default_color = "#0062b3"       # words without highlight
color_to_words = {
    '#d92425': ['宇宙での実験', '火星', '長期滞在', '宇宙服', '国際宇宙ステーション', '打ち上げる', 'はぶやさ', 'はぶやさ2', 'きぼう', '大西', 'ファン', '衛星', '観測', '宇宙飛行士', '実験', '宇宙科学研究所', '技術'] }

# create new color function to highlight words above in red
grouped_color_func = SimpleGroupedColorFunc(color_to_words, default_color)
wordcloud.recolor(color_func=grouped_color_func)

# image preview of wordcloud w/highlights
image2 = wordcloud.to_image()
image2.show()

# save wordcloud image w/highlights
wordcloud.to_file(path.join(d, "jaxa_word_highlight.png"))