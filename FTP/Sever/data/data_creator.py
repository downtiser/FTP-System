#Downtiser
import json
user_info = {
    'account_id':'noob',
    'password':'123abc',
    'disc_space':209715200
}

f = open('noob.json','w')

f.write(json.dumps(user_info))
f.close()