def len1 (sen1, sen2):
    # takes 2 sentences represented each by a list of strings,
    # returns the number of tokens of sen1 as an int
    return len(sen1)

def len2 (sen1, sen2):
    # takes 2 sentences represented each by a list of strings,
    # returns the number of tokens of sen2 as an int
    return len(sen2)

def lenDiff (sen1, sen2):
    # takes 2 sentences represented each by a list of strings,
    # returns the difference between the number of tokens (sen1 - sen2) as an int
    return len(sen1) - len(sen2)

def find1 (sen1, sen2, vocab):
    # takes 2 sentences and a vocabulary represented each by a list of strings,
    # returns the number of occurences of tokens of vocab in sen1 as an int
    return sum(el in vocab for el in sen1)
    
def find2 (sen1, sen2, vocab):
    # takes 2 sentences and a vocabulary represented each by a list of strings,
    # returns the number of occurences of tokens of vocab in sen2 as an int
    return sum(el in vocab for el in sen2)

def findDiff (sen1, sen2, vocab):
    # takes 2 sentences and a vocabulary represented each by a list of strings,
    # returns the difference between the number of occurences of tokens of vocab (sen1 - sen2) as an int
    return find1(sen1, sen2, vocab) - find2(sen1, sen2, vocab)
