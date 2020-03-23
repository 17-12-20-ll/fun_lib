d = {
    'p': 1,
    'n': 10,
    'one_src_id': 6,
    'name': ''
}
tmp_sql = []

for i in d:
    if i not in ['p', 'n']:
        if d[i]:
            if i == 'one_src_id':
                tmp_sql.append(f'a.one_src_id={d[i]}')
            if i == 'name':
                tmp_sql.append(f'a.name like "%{d[i]}%"')
print(' and '.join(tmp_sql))
