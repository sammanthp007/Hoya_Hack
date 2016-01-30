from twitter import *
access_token = '2750763448-o3z1B8QE09iHGXKb9YhGZKZiOoaADrUTri8cVD0'
access_token_secret = 'ghkX4dTPa98U3UsfuQgG6ASxGkBonPDa0ACUdjXkeKGTx'
consumer_key = 'pTQqksnWdlZac2oVz6zOnK4qJ'
consumer_key_secret = 'M29Ay2pM2nW6JlJWJINswpFVorINmHxX3FwWhYegPpJ9jpqB3D'
data = Twitter(auth=OAuth(access_token, access_token_secret, consumer_key, consumer_key_secret))

# Get your "home" timeline
# a = give_me.statuses.home_timeline()
# print (a)

# Get a particular friend's timeline
# dada = data.statuses.user_timeline(screen_name="bootsinasses92")
# print (dada)
def get_dic_of_friends():
	friends = data.friends.list()
	# print (type(friends))
	dic = {}
	for friend in friends['users']:
		username = friend['screen_name']
		description = friend['description']
		dic[username] = description
	return dic
