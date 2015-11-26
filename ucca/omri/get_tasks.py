import ucca_db

annotators = ["hagits", "henrybrice", "meirayan", "ayeldabay"]

for a in annotators:
    completed_tasks = ucca_db.get_tasks("/cs/++/phd/omria01/annotator_db_backup/huca_10_4.db", a)
    for t in completed_tasks:
        print(a+'\t'+'\t'.join([str(x) for x in t]))

