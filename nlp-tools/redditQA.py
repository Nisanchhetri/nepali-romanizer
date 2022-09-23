"""
Read from database question and answer pair
"""
import sqlite3


timeframe = '2017-03'
sql_transaction = []
start_row = 0
cleanup = 1000000

connection = sqlite3.connect('{}.db'.format(timeframe))
c = connection.cursor()

c.execute("SELECT parent, comment FROM parent_reply")
rows = c.fetchall()

question = open("train.from", mode='w',encoding='utf8')
reply = open("train.to", mode='w', encoding='utf8')

for index, row in enumerate(rows[:1000000]):
    # print('\n\n', index, '\tBody : ', row[0], '\nComment : ', row[1])
    question.write(row[0]+'\n')
    reply.write(row[1]+'\n')
    if index % 100000 == 0:
        print(index, 'pairs written to file')

question.close()
reply.close()

