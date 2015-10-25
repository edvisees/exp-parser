# script to evaluate the clusters
import sys
# python evaluate.py sample_test.out sample_test.gold_labels
#print "just type \" python evaluate.py sample_test.out sample_test.gold_labels\""
input = open(sys.argv[1], "r")
#input = open("./sample_test.out", "r")
gold = open(sys.argv[2], "r")
#gold = open("./sample_test.gold_labels", "r")


ansResult = []
sysClusters = []
goldResult = []
hit = 0
expected_ans = 0

for line in input:
    tokens = line.strip().split("\t")
    result = tokens[0]
    ansResult.append(result)
input.close()

gold_dict = dict({})
for line in gold:
    gold_ans = line.strip()
    goldResult.append(gold_ans)
    if gold_ans not in gold_dict:
        gold_dict[gold_ans] = 1
    else:
        gold_dict[gold_ans] += 1
gold.close()



# get accuracy
for i in range(0, len(goldResult)):
    if ansResult[i] != goldResult[i]:
        hit += 1
print "Accuracy =", 1 - hit/(len(goldResult) * 1.0)

# F1 Score Calculation Begin
res = dict({})
for i in range(len(ansResult)):
    count_list = [0] * 3  # [0] -> tp, [1] -> fp, [2] -> fn
    if not res.has_key(ansResult[i]):
        res[ansResult[i]] = count_list
    if not res.has_key(goldResult[i]):
        res[goldResult[i]] = count_list
    if ansResult[i] == goldResult[i]:
        res[ansResult[i]][0] += 1
    else:
        res[ansResult[i]][1] += 1
        res[goldResult[i]][2] += 1

f1_dict = dict({})
for key, value in res.items():
    if value[0] == 0 and value[1] == 0:
        precision = 0.
    else:
        precision = value[0]/((value[0] + value[1]) * 1.0)

    if value[0] == 0 and value[2] == 0:
        recall = 0.
    else:
        recall = value[0]/((value[0] + value[2]) * 1.0)
    if precision == 0 and recall == 0:
        f1 = 0.
    else:
        f1 = 2.0 * precision * recall / (precision + recall)
    f1_dict[key] = f1

    print '\n****** For ', key, '******'
    print 'F1 Score = ', f1
    print 'Precision = ', precision
    print 'Recall = ', recall

print "\n********************** Total F1 Score ********************"
f1_sum = 0.
for key, value in f1_dict.items():
    f1_sum += gold_dict[key] * value
print 'Weighted F1 Score = ', f1_sum/len(goldResult)
