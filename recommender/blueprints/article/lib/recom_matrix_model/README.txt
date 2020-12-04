def segment(text , mode = 'search' , HMM = True , rm_punch = True , rm_stopwords = True , rm_single_char = True , printout = False)

model = Doc2Vec(size=200, window=15, min_count=1, workers=4, alpha=0.025, min_alpha=0.01, dm= 0, hs= 1)
model.train(it, total_examples=model.corpus_count, epochs= 30)

// model 檔案過大 不上傳github