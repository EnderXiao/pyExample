# dicts.py
import json

path = r'c/hh/ss/hr/hr'
param = {'a': 1, 'b': 3, 'c': {"hh": {"n": [], "group": 3, "plat": 1, "ss": {"x": 1, "hr": {"y": 2, "hr": {"z": 3}}}}}}
add_param = {'group': 28, 'plat': 3}
path = path.split(r'/')
ll = param
for p in path:
    ll = ll.get(p)
    print(ll)

print('----分界线-----')
print(param['c']['hh']['ss']['hr']['hr'])
ll.update(add_param)
print('最终param')
s = json.dumps(param)
print(s)
