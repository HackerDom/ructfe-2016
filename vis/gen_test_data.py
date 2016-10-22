teamsCount = 300;

f = open('info','w')
f.write('{\n')
f.write('\t"teams": {')
strs = [];
for i in range(0, teamsCount):
	strs.append('"t' + str(i) + '": "team name ' + str(i) + '"')
f.write(", ".join(strs))
f.write('},\n\t"services": {"s1": "service name 1", "s2": "service name 2"}')
f.write('\n}')
f.close()


f = open('scoreboard','w')
f.write('{\n')
f.write('\t"table": {')
strs = [];
for i in range(0, teamsCount):
	strs.append('"t' + str(i) + '": "' + str(i) + '"')
f.write(", ".join(strs))
f.write('},\n\t"status": "1"')
f.write(',\n\t"round": "0"')
f.write('\n}')
f.close()