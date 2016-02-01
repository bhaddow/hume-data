import sqlite3, sys
from xml.etree.ElementTree import ElementTree, tostring, fromstring

#######################################################################################
# Returns the most recent xmls from db with a passage id pid and usernames
# (a list). The xmls are ordered in the same way as the list usernames.
#######################################################################################
def get_xml_trees(db, pid, usernames):
    con = sqlite3.connect(db)
    c = con.cursor()
    xmls = []
    for username in usernames:
        cur_uid = get_uid(db, username)
        c.execute("SELECT xml FROM xmls WHERE paid=? AND uid=? ORDER BY ts DESC", \
                  (pid, cur_uid))
        raw_xml = c.fetchone()
        if raw_xml == None:
            raise Exception("The user " + username + " did not submit an annotation for this passage")
        else:
            xmls.append(fromstring(raw_xml[0]))
    return xmls


def get_by_xids(db, xids):
    "Returns the passages that correspond to xids (which is a list of them)"
    con = sqlite3.connect(db)
    c = con.cursor()
    xmls = []
    for xid in xids:
        c.execute("SELECT xml FROM xmls WHERE id=?", (int(xid),))
        raw_xml = c.fetchone()
        if raw_xml == None:
            raise Exception("The xid " + xid + " does not exist")
        else:
            xmls.append(fromstring(raw_xml[0]))
    return xmls


def get_uid(db, username):
    "Returns the uid matching the given username."
    con = sqlite3.connect(db)
    c = con.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    cur_uid = c.fetchone()
    if cur_uid == None:
        raise Exception("The user " + username + " does not exist")
    return cur_uid[0]

def write_to_db(dbname, xml, new_pid, new_prid, username):
    con = sqlite3.connect(dbname)
    c = con.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    cur_uid = c.fetchone()
    if cur_uid == None:
        raise Exception("The user " + username + " does not exist")
    else:
        cur_uid = cur_uid[0]
    now = datetime.datetime.now()
    con.execute("INSERT INTO xmls VALUES (NULL, ?, ?, ?, ?, ?, 0, ?)", (xml, new_pid, prid, cur_uid, '', now))
    

def get_most_recent_xids(db, username):
    "Returns the most recent xids of the given username."
    cur_uid = get_uid(db, username)
    con = sqlite3.connect(db)
    c = con.cursor()
    c.execute("SELECT id, paid FROM xmls WHERE uid=? ORDER BY ts DESC", (cur_uid,))
    print(username)
    print("=============")
    r = c.fetchone()
    count = 0
    while r and count < 10:
        print(r)
        r = c.fetchone()
        count += 1


def get_passage(db, pid):
    "Returns the passages with the given id numbers"
    con = sqlite3.connect(db)
    c = con.cursor()
    c.execute("SELECT passage FROM passages WHERE id=?", (pid,))
    output = c.fetchone()
    if output == None:
        raise Exception("No passage with ID=" + pid)
    return output[0]



#Xget_most_recent_xids('huca.db', sys.argv[1])
