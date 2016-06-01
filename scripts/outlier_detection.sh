
echo 'Romanian'
echo ''

python compute_correlation_sent_len_diff_scores.py data/mturkDA/himl2015.en-ro.uccaids data/mturkDA/himl2015.en-ro.uccascores data/mturkDA/himl2015.en-ro.en data/mturkDA/himl2015.en-ro.trans.ro data/mturkDA/ad-stnd-seg-scores-10.en-ro.csv 15:20:25 0.34 10 ro_overlap_sents

echo ''
echo 'German'
echo ''

python compute_correlation_sent_len_diff_scores.py data/mturkDA/himl2015.en-de.uccaids data/mturkDA/himl2015.en-de.uccascores data/mturkDA/himl2015.en-de.en data/mturkDA/himl2015.en-de.trans.de data/mturkDA/ad-stnd-seg-scores-10.en-de.csv 15:20:25 0.34 10 de_overlap_sents



