import itertools
sList = ['verne','vern','passepartout','jules','jean','fogg','phileas']
#sList = ['JulesVern','JulesVerne','Jules Verne', 'Jules Vern']
#sList = ['Phileas Fogg','PhileasFogg']
#sList = ['Jean Passepartout','JeanPassepartout']

for s in sList:
    d = map(''.join, itertools.product(*zip(s.upper(), s.lower())))
    for i in d:
        print(i)
