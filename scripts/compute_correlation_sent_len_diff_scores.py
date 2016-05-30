import sys, pdb
import scipy.stats


def find_bin(threshs,val):
    """
    Returns the bin index (0 onwards) for the appropriate bin given threshs.
    """
    return [x[0] for x in enumerate(threshs + [10000]) if x[1] > val][0]
    

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("compute_correlation_sent_len_diff_scores.py <uccaids> <hume scores> <source sents> <trans sents> <DA scores> <length thresholds (:-delimited)>")
        sys.exit(-1)
    
    ucca_ids = [int(x.strip()) for x in open(sys.argv[1]).readlines()]
    hume = [float(x.strip()) for x in open(sys.argv[2]).readlines()]
    source_sent_lens = [len(x.strip().split()) for x in open(sys.argv[3]).readlines()]
    trans_sent_lens = [len(x.strip().split()) for x in open(sys.argv[4]).readlines()]
    da_scores = []
    for ind,l in enumerate(open(sys.argv[5])):
        if ind == 0:
            continue
        fields = l.strip().split()
        da_scores.append((int(fields[0]),float(fields[2])))

    threshs = [int(x) for x in sys.argv[6].split(':')]

    # bin the sents by sent length
    bins_source_len = [[] for x in threshs] + [[]]
    for sid, score in da_scores:
        bins_source_len[find_bin(threshs,source_sent_lens[sid])].append((sid,score,hume[sid]))

    pearson_by_bins_source = []
    for bin in bins_source_len:
        if bin == []:
            pearson_by_bins_source.append((None,0))
        else:
            pearson_by_bins_source.append((\
                scipy.stats.pearsonr([x[1] for x in bin], [x[2] for x in bin])[0],len(bin)))

    bins_trans_len = [[] for x in threshs] + [[]]
    for sid, score in da_scores:
        bins_trans_len[find_bin(threshs,trans_sent_lens[sid])].append((sid,score,hume[sid]))

    pearson_by_bins_trans = []
    for bin in bins_trans_len:
        if bin == []:
            pearson_by_bins_trans.append((None,0))
        else:
            pearson_by_bins_trans.append((\
                scipy.stats.pearsonr([x[1] for x in bin], [x[2] for x in bin])[0],len(bin)))

    print(pearson_by_bins_source)

    print(pearson_by_bins_trans)

    
