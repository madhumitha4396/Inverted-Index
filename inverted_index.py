import sys
d = {}
parameter = {}
parameter["corpus"] = sys.argv[1]
parameter["out"] = sys.argv[2]
parameter["in"] = sys.argv[3]

out = open(parameter["out"], 'a')
d_length = 0

def processFile():
    with open(parameter["corpus"], 'r') as document:
        for line in document:
            line = line.rstrip("\n")
            str = line.split("\t")
            for word in str[1]:
                tokens = str[1].split(" ")
            tokens = list(dict.fromkeys(tokens))
            for eachitem in tokens:
                if eachitem in d:
                    d[eachitem] += [str[0]]
                else:
                    d[eachitem] = [str[0]]

with open(parameter["corpus"], 'r') as document:
    d_tf = {}
    for line in document:
        line = line.split()
        if not line:
            continue
        d_tf[line[0]] = line[1:]

def get_postings_list():
    comparisons = 0
    result_and = []
    with open(parameter["in"], 'r') as f:
        lines = f.readlines()
        fcount = 0
        for l in lines:
            fcount += 1
        for line in lines:
            postingslist_of_terms = []
            line = line.rstrip("\n")
            for t in line.split():
                if t in d:
                    postinglist = d[t]
                    postingslist_of_terms.append(postinglist)
                    out.write('GetPostings\n')
                    out.write(t)
                    out.write("\n")
                    out.write('Postings list: ')
                    out.write((' '.join(postinglist) + "\n"))
            result_and, comparisons_and = daat_and(postingslist_of_terms, comparisons)
            tfidf_and = tf_idf_cal(result_and, line)
            out.write("DaatAnd\n")
            out.write((line))
            if "\n" not in line:
                out.write("\n")
            if len(result_and) != 0:                
                out.write('Results: ' + (' '.join(result_and) + "\n"))
                out.write('Number of documents in results: '+str(len(result_and))+ "\n")                
            else:
                out.write('Results: empty\n')
                out.write('Number of documents in results: 0\n')
            out.write('Number of comparisons: ' + str(comparisons_and) + "\n")
            out.write('TF-IDF\n')
            if len(tfidf_and) != 0:
                out.write('Results: ' + (' '.join(tfidf_and) + "\n"))
            else:
                out.write('Results: empty\n')
            result_or, comparisons_or = daat_or(postingslist_of_terms, comparisons)
            tfidf_or = tf_idf_cal(result_or, line)
            out.write("DaatOr\n")
            out.write((line))
            if "\n" not in line:
                out.write("\n")
            if len(result_or) != 0:
                out.write('Results: ' + (' '.join(result_or) + "\n"))
                out.write('Number of documents in results: '+str(len(result_or))+ "\n")
            else:
                out.write('Results: empty\n')
                out.write('Number of documents in results: 0\n')
            out.write('Number of comparisons: ' + str(comparisons_or) + "\n")
            out.write('TF-IDF\n')
            if len(tfidf_or) != 0:
                out.write('Results: ' + (' '.join(tfidf_or) + "\n"))
                out.write("\n")
            else:
                out.write('Results: empty\n')
                out.write("\n")
        fcount -= 1
        if fcount != 1:
            out.write("\n")
            
def do_comp_and(postings1, postings2, comparisons):
    res = []
    a = len(postings1)
    b = len(postings2)
    i = j = 0
    while i < a and j < b:
        if postings1[i] == postings2[j]:
            res.append(postings2[j])
            comparisons += 1
            i += 1
            j += 1
        elif postings1[i] < postings2[j]:
            comparisons += 1
            i += 1
        else:
            comparisons += 1
            j += 1
    return res, comparisons


def do_comp_or(postings1, postings2, comparisons):
    res = []
    a = len(postings1)
    b = len(postings2)
    i = j = 0
    while i < a and j < b:
        if postings1[i] == postings2[j]:
            res.append(postings1[i])
            comparisons += 1
            i += 1
            j += 1
        elif postings1[i] < postings2[j]:
            res.append(postings1[i])
            comparisons += 1
            i += 1
        else:
            res.append(postings2[j])
            comparisons += 1
            j += 1
    while i < a:
        res.append(postings1[i])
        i += 1
    while j < b:
        res.append(postings2[j])
        j += 1

    return res, comparisons

def daat_and(query_postings, comparisons):
    length = len(query_postings)
    res = query_postings[0]
    i = 1
    while i < length:
        res, comparisons_final = do_comp_and(res, query_postings[i], comparisons)
        comparisons = comparisons_final
        i = i+1
    return res, comparisons

def daat_or(query_postings, comparisons):
    res = []
    length = len(query_postings)
    res = query_postings[0]
    i = 1
    while i < length:
        res, comparisons_final = do_comp_or(res, query_postings[i], comparisons)
        comparisons = comparisons_final
        i = i+1
    return res, comparisons

def tf_idf_cal(result, lines):
    tf_idf_dict = {}
    y=[]
    for postings in result:
        local_idf = 0
        tf_idf = 0
        terms_in_doc = d_tf[postings]
        for query_term in lines.split():
            term_count = 0
            total_count = 0
            for token in terms_in_doc:
                total_count = total_count + 1
                query_term= query_term.strip()
                if (query_term == token):
                    term_count = term_count + 1
            term_freq = (term_count) / (total_count)
            l=0
            if "\n" in query_term:
                l=len(query_term)
                l=l-1
                query_term=query_term[0:l]
            x = d[query_term]
            x_len = len(x)
            d_length=len(d_tf)
            idf = d_length / x_len
            tf_idf = term_freq * idf
            local_idf = tf_idf + local_idf
        tf_idf_dict[postings] = local_idf

    tf_idf_list1 = sorted(tf_idf_dict.items(), key=lambda x: x[1])
    y = [x[0] for x in tf_idf_list1]
    y = list(reversed(y))
    return y


if __name__ == "__main__":
    processFile()
    get_postings_list()

























