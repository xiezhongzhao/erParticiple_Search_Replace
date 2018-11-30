from Synonyms import erSynonyms
import time

test_sent = input("请输入文本：")

strText, er_replace_index = erSynonyms(test_sent).text_synonyms()

print(strText)
print(er_replace_index)







































