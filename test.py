# -*- coding:utf-8 -*-
import os
import sqlite3

uid = '1952'
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'statistic', 'test.db')
conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_id (
            last_ticket_info_id   CHAR(50)
        );
        """)

cursor.execute("""
        INSERT INTO ticket_id  (last_ticket_info_id) VALUES
        (?)
    """, (uid))

res = cursor.execute("""
   SELECT 'last_ticket_info_id' FORM 'ticket_id'
""")
conn.commit()
conn.close()
print(res)