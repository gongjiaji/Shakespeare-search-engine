import json
from nltk.tokenize import word_tokenize
from nltk.stem.lancaster import LancasterStemmer
from nltk.corpus import stopwords
from ordered_set import OrderedSet

# 10 queries
expected = {
    "bunch": OrderedSet(['Henry IV', 'Measure for measure', 'Richard III']),
    "hi": OrderedSet(['Much Ado about nothing']),
    "kill": OrderedSet(['Henry IV', 'Henry VI Part 2', 'Henry VI Part 3', 'Alls well that ends well', 'As you like it', 'Antony and Cleopatra', 'Cymbeline', 'King John', 'Julius Caesar', 'King Lear', 'Loves Labours Lost', 'macbeth', 'Measure for measure', 'Merchant of Venice', 'A Midsummer nights dream', 'Much Ado about nothing', 'Othello', 'Pericles', 'Richard II', 'Richard III', 'Romeo and Juliet', 'Taming of the Shrew', 'Timon of Athens', 'Titus Andronicus', 'Twelfth Night', 'Henry V', 'Julius Caesar', 'Merry Wives of Windsor', 'Richard II', 'Richard III', 'Troilus and Cressida', 'Alls well that ends well', 'Merry Wives of Windsor', 'Much Ado about nothing', 'Pericles', 'The Tempest', 'Two Gentlemen of Verona', 'Coriolanus', 'Hamlet', 'Henry VIII', 'King John', 'A Winters Tale', 'Henry VI Part 1', 'A Comedy of Errors', 'Coriolanus', 'macbeth']),
    "rememberst": OrderedSet(['As you like it', 'The Tempest']),
    "slightest": OrderedSet(['As you like it', 'Much Ado about nothing', 'Henry IV']),
    "exclamation": OrderedSet(['Henry VIII', 'Much Ado about nothing', 'King John']),
    "bug": OrderedSet(['Henry VI Part 3', 'A Winters Tale']),
    "homes": OrderedSet(['Coriolanus', 'King John']),
    "eating": OrderedSet(['Henry IV', 'Richard II', 'Titus Andronicus', 'Twelfth Night', 'Richard II', 'Timon of Athens', 'Henry VI Part 2', 'Two Gentlemen of Verona', 'A Winters Tale', 'Julius Caesar', 'Measure for measure']),
    "childrens": OrderedSet(['Henry VI Part 2', 'macbeth', 'Richard III', 'Henry IV', 'Coriolanus', 'Measure for measure', 'Richard II', 'Romeo and Juliet', 'Henry VI Part 1', 'Henry VIII'])
}

def stemmed_expected(dataset):
    dic = {}
    for x in dataset.keys():
        y = LancasterStemmer().stem(x)
        dic[y] = dataset[x]
    return dic

# my search engine
def get_predicted(keyword):
    try:
        result = index[keyword]
    except KeyError:
        print('no such key.')
        result = set()
    return result

# elastic search
def get_actual(keyword):
    try:
        dataset = stemmed_expected(expected)
        result = dataset[keyword] 
    except KeyError:
        print('no such key..')
        result = set()
    return result

def cal_PK(keyword):
    k = 1
    pk_sum = 0
    while k<= len(get_actual(keyword)):
        predicted = get_predicted(keyword)
        actual = OrderedSet(get_actual(keyword)[:k])
        corret = len(predicted & actual)
        precision = corret/float(k)
        pk_sum += precision
        print("k="+str(k)+"\n"+ "predicted:"+str(predicted)+"\n"+"actual"+str(actual)+"\n"+"precision"+str(precision))
        k += 1
    try:
        pk = format(pk_sum/(k-1), '.2f')
    except ZeroDivisionError:
        pk = 0.00
    
    print("pk of *"+keyword+"* is "+str(pk)+"\n\n\n")
    return pk

def cal_map(dataset):
    map_value = 0
    for keyword in dataset.keys():
        keyword = LancasterStemmer().stem(keyword)
        map_value += float(cal_PK(keyword))
    map_value = format(map_value/len(dataset.keys()), '.2f')
    print('MAP: '+map_value)
    return map_value

print("step 1...Read json file")

shake = []
with open("shakespeare_6.0.json","r") as f:
    for line in f: # each line contains a json string
        shake_raw = json.loads(line)
        # remove all the unrelated lines
        if("index" in shake_raw):
            pass
        else:
            shake.append(shake_raw)

print("step 2...Indexing, It takes up to 5 minutes...")

play = ""
dic = {}
for s in shake:  # s : {"type":"scene","line_id":2,"play_name":"Henry IV","speech_number":"","line_number":"","speaker":"","text_entry":"SCENE I. London. The palace."}
    if(play != s["play_name"]):
        content = set()
    play = s["play_name"]

    tokens = word_tokenize(s["text_entry"])  # tokens = ["SCENE", "I.", "London", "The" ,"palace"]
    english_punctuations = [',', '.', ':', ';', '?',
                            '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
    for x in tokens:
        x = x.lower()
        x = LancasterStemmer().stem(x)
        if(x not in stopwords.words('english')):
            if(x not in english_punctuations):
                content.add(x)        
    dic[play] = content

index = {} # { token -> play_name set }
for k in dic.keys():
    for token in dic[k]:
        if(token in index.keys()):
            index[token].add(k)
        else:
            index[token] = set()
            index[token].add(k)

print('step 3...Searching')

print('step 4...Evaluation')

cal_map(expected)

