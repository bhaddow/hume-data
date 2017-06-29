import sqlite3, sys, ucca_db, ucca.convert
from xml.etree.ElementTree import ElementTree, tostring, fromstring


def get_all_users(con):
    c = con.cursor()
    c.execute("SELECT id,username FROM users WHERE id >= 10")
    return c.fetchall()

def monitor_annotators(con):
    c = con.cursor()
    progress = dict()  #maps uid to percent of annotated tokens
    all_users = get_all_users(con)
    user_count = 0

 
    for user in all_users:
        c.execute("SELECT xml,paid FROM xmls WHERE uid=? ORDER BY ts DESC", (user[0],))
        user_count += 1
        r2 = c.fetchone()
        if r2 is not None:
            cur_xml = fromstring(r2[0])
            try:
                ucca_dag = ucca.convert.from_site(cur_xml)
            except Exception as e:
                print("skipping "+str(user[0])+" "+str(user[1])+" "+str(r2[1]))
                user_count -= 1
                continue
            terminals = ucca_dag.layer("0").words
            num_terminals = len(terminals)
            num_no_parents = len([x for x in terminals if not x.parents[0].parents])
            progress[user[1]] = 1 - 1.0 * num_no_parents / num_terminals

    avg_progress = 1.0 * sum(progress.values()) / user_count
    print("Avg progress: "+str(avg_progress))
    print("Num users: "+str(user_count))
    for prog in progress.values():
        print(prog)

def num_scenes(con):
    "Computes the percentage of the scenes out of the submitted passages"
    all_users = get_all_users(con)
    
    # map the passage id to the total number of scenes, units and terminals
    total_scenes = dict() 
    total_units = dict()
    total_terminals = dict()
    
    c = con.cursor()
    for user in all_users:
        c.execute("SELECT xml, paid FROM xmls WHERE uid=? AND status=? ORDER BY ts DESC", (user[0],1))
        res = c.fetchone()
        if res is not None:
            cur_xml = fromstring(res[0])
            try:
                ucca_dag = ucca.convert.from_site(cur_xml)
            except Exception as e:
                continue

            total_terminals[res[1]] = total_terminals.get(res[1],0) + len(ucca_dag.layer("0").words)
            total_scenes[res[1]] = total_scenes.get(res[1],0) + len([x for x in ucca_dag.layer('1').all if x.tag == 'FN' and x.is_scene()])
            total_units[res[1]] = total_units.get(res[1],0) + len([x for x in ucca_dag.layer('1').all])

    for paid in range(20,25):
        print(paid)
        print("terminals: " + str(total_terminals.get(paid,0)) + " , scenes: " + str(total_scenes.get(paid,0)) + " , units: " + str(total_units.get(paid,0)))
        print()

def print_terminals(con):
    c = con.cursor()
    all_users = get_all_users(con)
 
    for user in all_users:
        c.execute("SELECT xml FROM xmls WHERE uid=? AND paid=? ORDER BY ts DESC", (user[0],23))
        res = c.fetchone()
        if res is not None:
            cur_xml = fromstring(res[0])
            try:
                ucca_dag = ucca.convert.from_site(cur_xml)
            except Exception as e:
                continue
            #for w in ucca_dag.layer("0").words:
            #    sys.stdout.write(w.text + "." + w.ID + " ")
            scene = find_minimal_scene_parent(ucca_dag, "0.58")
            if scene != None:
               print("--" + scene.to_text())
                

def pretty_print(u):
    "prints a layer1 node including all its sub-structure"
    if u.parents == None:
        print("TOP")
    else:
        print([x.tag for x in u._incoming.tag])
    

def find_minimal_scene_parent(P, terminal_id):
    "given a passage, it returns its minimal parent which is a scene"
    terminal_id = int(terminal_id.split('.')[1])
    t = P.layer("0").all[terminal_id]
    parents = t.parents
    while parents != []:
        par = None
        for par in parents:
            if par.tag == 'FN':
                break
        if par == None:
            break
        if par.is_scene():
            return par
        parents = par.parents
    return None
    
def admin_scenes(con):
    "returns the number of scenes the admin passages have"
    c = con.cursor()

    for paid in range(20,25):
        c.execute("SELECT xml FROM xmls WHERE uid=? AND paid=? ORDER BY ts DESC", (2,paid))
        res = c.fetchone()
        if res is not None:
            cur_xml = fromstring(res[0])
            try:
                ucca_dag = ucca.convert.from_site(cur_xml)
            except Exception as e:
                continue
            num_term = len(ucca_dag.layer("0").words)
            num_units = len(ucca_dag.layer("1").all)
            num_scenes = len([x for x in ucca_dag.layer('1').all if x.tag == 'FN' and x.is_scene()])

            print(paid)
            print("Terminals: " + str(num_term) + " Units: " + str(num_units) + " Scenes: " + str(num_scenes))


#############
# MAIN
#############

con = sqlite3.connect('/cs/++/phd/omria01/course_db_backup_2Apr/huca.db.8_4')
#monitor_annotators(con)
#num_scenes(con)
#admin_scenes(con)
print_terminals(con)


