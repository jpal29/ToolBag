headers = ["name","level","value"]

vals1 = ["Some long name", "a level", "a value"]

vals2 = ["An even longer name", "another level", "another value"]

max_lens = [len(str(max(i, key=lambda x: len(str(x))))) for i in zip(headers, vals1, vals2)]
print(max_lens)
for item in zip(headers, vals1, vals2):
	print(item)

for row in (headers, vals1, vals2):
	print(row)
	print('|'.join('{0:{width}}'.format(x, width=y) for x, y in zip(row, max_lens)))
