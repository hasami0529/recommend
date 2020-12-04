#required

import json
import re
import jieba
import jieba.analyse
from gensim.models import Doc2Vec

model = Doc2Vec.load(
    'recommender/blueprints/article/lib/recom_matrix_model/recom_matrix.model')
# jieba.load_userdict('lib/jieba_materials/traditional_chinese.txt')


def infer_vec(words, _format='list'):
    """   
    Arguments:
        words {list} -- list of words after segment
    
    Keyword Arguments:
        _format {str} -- json or list (default: {'list'})
    
    Returns:
        list of json string -- vector
    """
    '''
    words = list of string
    把list of words 轉成向量
    _formate = ['json' , 'list' ] if none it will be numpy.array
    '''
    ivec = model.infer_vector(doc_words=words, steps=20, alpha=0.025)
    if _format == 'json':
        ivec = ivec.tolist()
        ivec = json.dumps(ivec)
    elif _format == 'list':
        ivec = ivec.tolist()
    return ivec


def segment(text,
            mode='tf_idf',
            rm_punch=True,
            rm_stopwords=True,
            rm_single_char=True,
            printout=False):
    """斷詞
    
    Arguments:
        text {str} -- 要斷的文章
    
    Keyword Arguments:
        mode {str} -- 詳見jieba (default: {'search'})
        HMM {bool} -- 詳見jieba (default: {True})
        rm_punch {bool} -- 是否移除標點 (default: {True})
        rm_stopwords {bool} -- 是否移除停用詞, jieba裡面有停用詞表 (default: {True})
        rm_single_char {bool} -- 是否移除一個字元的字詞 (default: {True})
        printout {bool} -- 是否印出結果 (default: {False})
    
    Returns:
        list -- list of words
    """

    def remove_punctuation(line):

        #數字去掉
        rule = re.compile(r'[^a-zA-Z\u4e00-\u9fa5]')
        line = rule.sub(' ', line)
        return line

    def remove_stopwords(text):
        with open(
                'recommender/blueprints/article/lib/jieba_materials/stopwords.txt',
                'r',
                encoding='utf-8') as f:
            stopwords = f.read().split('\n')
        text = [i for i in text if i not in stopwords]
        return text

    #去標點 數字
    if rm_punch:
        text = remove_punctuation(text)

    #斷詞

    if mode == 'default':
        cut = jieba.lcut
        words = cut(text)
    elif mode == 'search':
        cut = jieba.lcut_for_search
        words = cut(text)
    elif mode == 'tf_idf':
        words = jieba.analyse.extract_tags(text, topK=30, withWeight=False)

    if rm_stopwords:
        words = remove_stopwords(words)

    if rm_single_char:
        words = [i for i in words if len(i) > 1]

    if printout:
        print('/'.join(words))

    return words
