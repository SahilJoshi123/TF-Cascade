import MySQLdb
import json
import collections

conn=MySQLdb.connect(host='localhost',user='root',passwd='password')
#conn = pyodbc.connect(connstr)
cursor = conn.cursor()
cursor.execute('use tfcascade;')


cursor.execute("""
            SELECT CHAIN_ID, CHAIN, CHAIN_LENGTH
            FROM tbl_chains
            """)
rows = cursor.fetchall()

# Convert query to objects of key-value pairs
d = dict()
for row in rows:
    d[str(row[0])] = [str(row[0]), row[1].strip(), row[2].strip()]

objects_file = 'Chains.json'
f = open(objects_file,'w')
j = json.dumps(d)
print >> f, j



#*********************************************************************************************************************
cursor.execute("""
            SELECT CHAIN_ID, CHAIN, CHAIN_LENGTH
            FROM tbl_genechains
            """)
rows = cursor.fetchall()

# Convert query to objects of key-value pairs
d2 = dict()
for row in rows:
    d2[str(row[0])] = [str(row[0]), row[1].strip(), row[2].strip()]

objects_file = 'Genes.json'
f = open(objects_file,'w')
j2 = json.dumps(d2)
print >> f, j2



#*********************************************************************************************************************
cursor.execute("""
            SELECT *
            FROM tbl_knowledge_experiment
            """)
rows = cursor.fetchall()
# Convert query to objects of key-value pairs


d3 = dict()
for row in rows:
    d3[str(row[0])] = [str(row[0]), row[1].strip(), row[2].strip(), row[3].strip(), row[4].strip(), row[5].strip(), row[6].strip(), str(row[7]), row[8].strip()]
    


objects_file = 'Knowledge.json'
f = open(objects_file,'w')
j3 = json.dumps(d3)
print >> f, j3

conn.close()