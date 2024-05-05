import sqlite3
import json

conn = sqlite3.connect('nodedatabase.db', check_same_thread=False)
c = conn.cursor()

def create_table(table_name):
    c.execute(f"""CREATE TABLE IF NOT EXISTS {table_name}
                  (id TEXT, label TEXT, apps TEXT, summary TEXT, long_summary TEXT, transcript TEXT, entities TEXT, date TEXT, temp BOOLEAN, hidden BOOLEAN)""")

def delete_table(table_name):
    c.execute(f"DROP TABLE IF EXISTS {table_name}")

def insert_data(table_name, data):
    create_table(table_name)
    c.execute(f"INSERT INTO {table_name} (id, label, apps, summary, long_summary, transcript, entities, date, temp, hidden) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(data.values()))
    conn.commit()

def get_all_data(table_name):
    create_table(table_name)
    c.execute(f"SELECT * FROM {table_name}")
    return c.fetchall()

def delete_data(table_name, id):
    c.execute(f"DELETE FROM {table_name} WHERE id=?", (id,))
    conn.commit()

if __name__ == "__main__":
    from modeling.ner import get_entities
    nodes = get_all_data("nodes")
    long_summaries = [node[4] for node in nodes]
    entities = [get_entities(long_summary)[1] for long_summary in long_summaries]
    delete_table("nodes")
    for i in range(len(nodes)):
        node = list(nodes[i])
        node[6] = entities[i]
        insert_data("nodes", node)