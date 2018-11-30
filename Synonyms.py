#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'将儿话音转换为书面语言模块'

__author__ = '谢中朝'
__copyright__   = "Copyright 2018, KINGSOFT"
__license__ = "GPL"
__version__ = "1.0.0"
__email__ = "s_xiezhongzhao@wps.cn"
__status__ = "Production"


import jieba
import ppl

class erSynonyms:

    # 设置文件路径和初始化
    def __init__(self, input_text):
        self.text_origin = input_text
        self.er_path = "./voc2.txt"
        self.twoWordsPath = "./TwoWords.txt"

        print("loading...")
        jieba.initialize()
        self.content2Jieba(self.add_Quotation_Content(self.text_origin))  # 将引号内容加入结巴词典
        self.text_list = self.participle(self.text_origin) # 将文本进行分词操作
        self.er_words = self.er_index(self.text_list) # 搜索带儿的分词
        self.er_false_words = self.read_er_false() # 读取带儿的非儿话词
        self.com_dic, self.er_quota = self.match_er_false(self.er_false_words, self.er_words, self.text_list) # 匹配非儿话词典和带儿词典，不需要替换的儿话词
        self.er_replace_participle = self.er_needed_replaced(self.er_words, self.com_dic, self.er_quota) # 获得需要替换的儿话音分词
        self.model = ppl.ppl()
        print("loading finished")

    # 提取引号的内容
    def add_Quotation_Content(self, text_origin):
        count = 0  # 记录字符个数
        index_front = 0  # 上引号索引
        index_end = 0  # 下引号索引
        quotation = []  # 带引号的列表

        for str in text_origin:
            if (str == u'“'):
                index_front = count
            if (str == u'”'):
                index_end = count
            if (index_front < index_end):
                quotation.append(text_origin[index_front + 1:index_end])
                index_front = 0
                index_end = 0
            count += 1

        return quotation

    # 将引号内容加入结巴词典
    def content2Jieba(self, Quotation):
        for content in Quotation:
            jieba.add_word(content)

    # 将文本进行分词操作
    def participle(self, test_origin):
        words = jieba.cut(test_origin)
        text_list = [list(jieba.cut(item_text, cut_all=False)) for item_text in words]
        return text_list

    # 搜索带儿的分词
    def er_index(self, text_list):
        num_word = 0
        er_words = {}

        for word in text_list:
            for str in word[0]:
                if (str == u'儿'):
                    er_words.setdefault("".join(text_list[num_word]), []).append(num_word)
                    continue
            num_word += 1
        return er_words

    # 读取带儿的非儿话词
    def read_er_false(self):
        er_false_words = {}
        num_false_words = 0
        with open(self.er_path, encoding='utf-8') as f:
            for line in f.readlines():
                er_false_words.setdefault(line.strip('\n'), []).append(num_false_words)
                num_false_words += 1
        return er_false_words

    # 匹配非儿话词典和带儿词典，不需要替换的儿话词
    def match_er_false(self, er_false, er_true, text_list):
        er_quota = {}  #检测引号内的带儿分词
        for key, value in er_true.items():
            for val in value:
                if val >= 1 and val < (len(text_list)-1):
                    if("".join(text_list[val-1]) == u'“') & ("".join(text_list[val+1]) == u'”'):
                        er_quota.setdefault("".join(key), []).append(val)

        com_dic = er_false.keys() & er_true.keys() #匹配非儿话词典和带儿词典

        return list(com_dic), er_quota

    # 得到每个字符的索引
    def get_str_index(self, text_list, key, val):
        str_index = 0
        for i in range(val):
            str_index += len(text_list[i])

        return 0

    # 获得需要替换的儿话音分词
    def er_needed_replaced(self, er_words , com_dic, er_quota):
        for key, val in er_words.items():  #删除儿话音分词中不需要替换的儿话分词(带引号儿话词)
            for key_q, val_q in er_quota.items():
                if key == key_q:
                    for i in val_q:
                        val.remove(i)

        ##检验er_words字典中val为空的key
        for i in er_words.copy():
            if not er_words[i]:
                er_words.pop(i)

        ##删除不需要替换的儿话音分词
        for i in com_dic:
            er_words.pop(i)

        return er_words

    # 替换儿话分词的候选词
    def candidate_word(self, key):
        candidate_list = []
        with open(self.twoWordsPath, 'r+', encoding='utf-8') as f:
            for line in f.readlines():
                line = line.strip().strip('\n')

                if(key[1] == u'儿'): #如果儿字在后面
                    key_del = key.strip(u'儿')
                    if(key_del == line[0]):
                        candidate_list.append(line)

        return candidate_list

    # 获得最终同义替换后的样本
    def text_synonyms(self):

        strText = ''  # 定义字符串
        text_copy = self.text_list.copy() #复制原始文本
        er_replace_index = [] #存储格式：{'昨儿': (0, 1, '昨日')}

        for key, value in self.er_replace_participle.items():

            if (len(key) == 1):
                # 检测到单个'儿'分词，在文本中直接删除
                for val in value:
                    self.text_list[val].pop()
                    str_index = 0
                    for i in range(val):
                        str_index += len("".join(text_copy[i]))
                    er_replace_index.append((key, str_index, ''))

            elif (len(key) == 2):

                punc = "！？｡＂＃＄％＆＇（）＊＋，,－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."
                punc = list(punc)

                candidate_list = self.candidate_word(key)
                # print(candidate_list)
                # exit()

                candidate_ppl_text = []
                scores = {}
                for candi_word in candidate_list:  # 运用ppl选出最有可能的候选词

                    self.text_list[value[0]] = candi_word#用候选词替换儿话分词

                    index_start = value[0] #需要替换的儿话分词的索引
                    index_end = value[0]
                    candidate_text = []

                    if(index_start == 0):
                        index_start = 0
                    else:
                        while ("".join(self.text_list[index_start]) not in punc):
                            index_start -= 1
                            if(index_start == 0):
                                index_start = 0
                                break

                    while ("".join(self.text_list[index_end]) not in punc):
                        index_end += 1
                        if(index_end >= len(self.text_list)):
                            index_end = len(self.text_list)
                            break

                    text = self.text_list[index_start:index_end] #以标点为标准选取有候选词的最短句子
                    # print(text)
                    for i,ele in enumerate(text.copy()): #删除候选句子中的标点
                        if "".join(ele) in punc:
                            text.pop(i)

                    # print(text)
                    for i in text:
                        candidate_text.append("".join(i))

                    candidate_ppl = "".join(candidate_text)
                    candidate_ppl_text.append(candidate_ppl)
                    scores[candi_word] = self.model.get_ppl(candidate_ppl)#将候选词的句子采用ppl打分

                scores = sorted(scores.items(), key=lambda item: item[1])  # value值从小到大进行排序

                if len(scores) != 0:
                    for val in value:
                        self.text_list[val] = scores[0][0] # 同义词替换
                        str_index = 0
                        for i in range(val):
                            str_index += len("".join(text_copy[i]))
                        er_replace_index.append((key, str_index, str_index + len(key) - 1, scores[0][0]))
                # print(er_replace_index)

            elif (len(key) == 3):
                # 删除三个字符中的'儿'字
                key_del = key.strip(u'儿')
                for val in value:
                    self.text_list[val] = key_del

            else:
                # 其他特殊情况处理
                pass

        #将列表元素转化为字符并连接在一起
        for item in self.text_list:
            strText += "".join(item)

        return strText, er_replace_index





























