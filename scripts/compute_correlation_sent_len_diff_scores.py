import sys, pdb, math
import numpy as np
import scipy.stats
import scipy.spatial.distance as distance

def find_bin(threshs,val):
    """
    Returns the bin index (0 onwards) for the appropriate bin given threshs.
    """
    return [x[0] for x in enumerate(threshs + [10000]) if x[1] > val][0]
    

if __name__ == "__main__":
    if len(sys.argv) not in [9,10]:
        print("compute_correlation_sent_len_diff_scores.py <uccaids> <hume scores> <source sents> <trans sents> <DA scores> <length thresholds (:-delimited)> <ordinal threshold> <num outliers> <overlap sents>")
        sys.exit(-1)

    ordinal_thresh = float(sys.argv[7])
    num_outliers = int(sys.argv[8])
    
    ucca_ids = [int(x.strip()) for x in open(sys.argv[1]).readlines()]
    hume = [float(x.strip()) for x in open(sys.argv[2]).readlines()]
    source_sents = [x.strip() for x in open(sys.argv[3]).readlines()]
    trans_sents = [x.strip() for x in open(sys.argv[4]).readlines()]
    source_sent_lens = [len(x.split()) for x in source_sents]
    trans_sent_lens = [len(x.split()) for x in trans_sents]
    if len(sys.argv) > 9:
        overlap_sentids = [int(x.strip()) for x in open(sys.argv[9]).readlines()]
    else:
        overlap_sentids = None
    
    da_scores = []
    for ind,l in enumerate(open(sys.argv[5])):
        if ind == 0:
            continue
        fields = l.strip().split()
        da_scores.append((int(fields[0]),float(fields[2]))) # (sid,da score)

    print([ucca_ids[x[0]] for x in da_scores])

    threshs = [int(x) for x in sys.argv[6].split(':')]

    # bin the sents by sent length
    bins_source_len = [[] for x in threshs] + [[]]
    for sid, score in da_scores:
        if overlap_sentids is None or ucca_ids[sid] in overlap_sentids :
            bins_source_len[find_bin(threshs,source_sent_lens[sid])].append((sid,score,hume[sid],ucca_ids[sid])) # (sid, DA score, hume score, ucca ID)

    pearson_by_bins_source = []
    for bin in bins_source_len:
        if bin == []:
            pearson_by_bins_source.append((None,0))
        else:
            pearson_by_bins_source.append((\
                scipy.stats.pearsonr([x[1] for x in bin], [x[2] for x in bin])[0],len(bin)))
            
    bins_trans_len = [[] for x in threshs] + [[]]
    for sid, score in da_scores:
        if overlap_sentids is None or ucca_ids[sid] in overlap_sentids:
            bins_trans_len[find_bin(threshs,trans_sent_lens[sid])].append((sid,score,hume[sid],ucca_ids[sid]))

    pearson_by_bins_trans = []
    for bin in bins_trans_len:
        if bin == []:
            pearson_by_bins_trans.append((None,0))
        else:
            pearson_by_bins_trans.append((\
                scipy.stats.pearsonr([x[1] for x in bin], [x[2] for x in bin])[0],len(bin)))
    
    print(pearson_by_bins_source)
    print(pearson_by_bins_trans)
    
    # find outliers: vertical distnace
    """
    for index,bin in enumerate(bins_source_len):
        if bin == []:
            print('===== Bin '+str(index)+' empty ========')
        else:
            print('===== Bin '+str(index)+' ========')
            slope, intercept, r_value, p_value, std_err = \
                   scipy.stats.linregress([x[1] for x in bin], [x[2] for x in bin])
            for x in bin:
                diff = math.pow(slope * x[1] + intercept - x[2],2)
                if diff > dist_thresh:
                    print(x[3],source_sents[x[0]],x[0],x[1])
    """
    
    # find distance in terms of ordinals
    """
    for index,bin in enumerate(bins_source_len):
        if bin == []:
            print('===== Bin '+str(index)+' empty ========')
        else:
            print('===== Bin '+str(index)+' ========')
            slope, intercept, r_value, p_value, std_err = \
                   scipy.stats.linregress([x[1] for x in bin], [x[2] for x in bin])
            for x in bin:
                diff = math.pow(slope * x[1] + intercept - x[2],2)
                if diff > dist_thresh:
                    print(x[3],source_sents[x[0]],x[0],x[1])
    """
    
    # find distnace in terms of ordinals (binned)
    """
    ordinal_thresh = 0.5
    for index,bin in enumerate(bins_source_len):
        if bin == []:
            print('===== Bin '+str(index)+' empty ========')
        else:
            bin_size = len(bin)
            print('===== Bin '+str(index)+' ======== '+str(bin_size))
            ords1 = np.array([x[1] for x in bin]).argsort().argsort()
            ords2 = np.array([x[2] for x in bin]).argsort().argsort()
            for ord1,ord2,x in zip(ords1,ords2,bin):
                if 1.0 * np.absolute(ord1 - ord2) / bin_size > ordinal_thresh:
                    print(ord1,ord2)
                    t = (x[3],source_sents[x[0]],trans_sents[x[0]],x[0],x[1],x[2])
                    print('\t'.join([str(x) for x in t]))
    """
    
    # All sentences, ordinal outliers
    all_sents = []
    for bin in bins_source_len:
        all_sents.extend(bin)

    print(scipy.stats.pearsonr([x[1] for x in all_sents], \
                               [x[2] for x in all_sents]))

    
    #print('===== All Bins Ordinal Outliers ======== '+str(len(all_sents)))
    ords1 = np.array([x[1] for x in all_sents]).argsort().argsort()
    ords2 = np.array([x[2] for x in all_sents]).argsort().argsort()
    print('\t'.join(['ordinal by DA', 'ordinal by HUME', 'source sentnece', 'translation','SID','DA score','HUME score','UCCA ID']))
    for ord1,ord2,x in zip(ords1,ords2,all_sents):
        if 1.0 * np.absolute(ord1 - ord2) / len(all_sents) > ordinal_thresh:
            t = (ord1,ord2,source_sents[x[0]],trans_sents[x[0]],x[0],x[1],x[2],x[3])
            print('\t'.join([str(z) for z in t]))


    # All sentences, 3-NN outliers

    # compute the 3 NNs for each point (self excluded), and their average distance
    # find the points with the highest / lowest distance
    print('\nk-NN analysis\n')
    k = 3
    X = np.transpose(np.array([[x[1] for x in all_sents],[x[2] for x in all_sents]]))
    D = distance.squareform(distance.pdist(X, 'euclidean'))
    proximity = np.sum(np.partition(D,k+1)[:,:(k+1)],axis=1)
    proximity_ords = proximity.argsort().argsort()
    print('\t'.join(['source sentnece', 'translation','SID','DA score','HUME score','UCCA ID']))
    
    for outlier_ind in reversed(range(len(proximity_ords)-num_outliers,len(proximity_ords))):
        list_index = list(proximity_ords).index(outlier_ind)
        x = all_sents[list_index]
        t = (source_sents[x[0]],trans_sents[x[0]],x[0],x[1],x[2],x[3])
        print('\t'.join([str(z) for z in t]))


