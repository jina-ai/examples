from sent_chunkspliter import Sent2Chunk


s = Sent2Chunk()
print(s.punct_chars)
p = s._slit_pat
print(p)
str1 = "我想唱一首歌给我们祝福，唱完了我会一个人住。我以为。"
r = s.craft(str1)

print(r)