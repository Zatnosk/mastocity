from mastodon import StreamListener
import re
import time

state = {
	'mastodon': None,
	'data': None
}

class StatusListener(StreamListener):
	def __init__(self, mastodon, data):
		self.mastodon = mastodon
		self.data = data
		state['mastodon'] = mastodon
		state['data'] = data

	def on_update(self, status):
		self.data.post_status(status)

class NotifListener(StreamListener):
	def __init__(self, mastodon, data):
		self.mastodon = mastodon
		self.data = data
		state['mastodon'] = mastodon
		state['data'] = data

	def on_notification(self, notification):
		if notification['type'] != 'mention':
			return
		NotifAnalyzer(notification['status'], self.mastodon, self.data)

class Cache():
	instance = None

	def __init__(self):
		self.cache = dict()

	@classmethod
	def _get_instance(cls):
		if not cls.instance:
			cls.instance = cls()
		return cls.instance

	@classmethod
	def set(cls, status):
		self = cls._get_instance()
		self.cache[str(status.status['id'])] = status,time.time()

	@classmethod
	def get(cls, id):
		self = cls._get_instance()
		status, t = self.cache.get(str(id),(None,0))
		if status and t > time.time() - 3600:
			#only return cached values less than an hour old
			return status
		else:
			return None

class NotifAnalyzer():
	own_account = 'unrealestate'
	own_server = 'manowar.social'
	re_buy = re.compile('buy a house');
	re_move = re.compile('move in with');
	re_move_target = re.compile('move in with .*?@([^@ ]+(@[^@ ]+)?)')
	re_yes = re.compile('yes');

	is_analyzed = False
	content_lower = None
	content_flat = None
	url = None
	name = None
	target = None
	type = None
	parent = None

	def __init__(self, status, mastodon, data):
		self.status = status
		self.mastodon = mastodon
		self.data = data
		Cache.set(self)

	def analyse(self):
		if self.is_analyzed or self.is_mine(): return
		self.is_analyzed = True
		content_lower = self.status['content'].lower()
		if self.re_buy.search(content_lower):
			self.type = 'buy'
		elif self.re_move.search(content_lower):
			self.type = 'move'
			self.target = self._parse_move()
		elif self.re_yes.search(content_lower):
			self.type = 'yes'
		self.url = self.status['account']['url']
		name = self.status['account']['acct']
		if '@' not in name:
			name += '@'+self.own_server
		self.name = '@'+name

	def reply(self):
		if self.type == 'buy':
			self._reply_buy()
		elif self.type == 'move':
			self._reply_move()
		elif self.type == 'yes':
			self._reply_yes()

	def _reply_buy(self):
		house = self.data.get_house(self.url)
		if house != None:
			x,y,_,_ = house
			text = "{} You already have a house here:\n".format(self.name)
		else:
			x,y = data.find_random_spot()
			data.build_house({
				'x':x,
				'y':y,
				'owner':self.name,
				'url':self.url
			})
			text = "{} Your new house is here:\n".format(self.name)
		text += "http://zatnosk.dk/playground/mastocity/?x={}&y={}".format(x,y)
		self._send_reply(text)
	
	def _reply_move(self):
		if not self.target: return
		house = self.data.get_house(self.target['url'])
		if house == None:
			text = "{} It doesn't look like @{} has a house around here.".format(self.name, self.target['name'])
		if house != None:
			text = "{} You've requested to move in with @{}.\n\n".format(self.name, self.target['name'])
			text += "Before you can move in, someone from the house must answer YES to this toot.\n"
			text += "Current residents:\n"
			residents = self.data.get_residents(house[0],house[1])
			for (resident,url) in residents:
				text += resident+"\n"
		self._send_reply(text)
		
	def _reply_yes(self):
		parent = self._get_parent()
		if not parent \
			or not parent.is_mine() \
			or not parent.status['in_reply_to_id']: return
		grandparent = parent._get_parent()
		if not grandparent: return
		grandparent.analyse()
		if grandparent.type != 'move': return
		target = grandparent.target
		text = "Congratulations"
		for mention in parent.status['mentions']:
			if grandparent.url == mention['url']: mover_mentioned = True
			if target['url'] == mention['url']: target_mentioned = True
			text += ", @"+mention['acct']
		if not mover_mentioned or not target_mentioned: return
		house = self.data.get_house(target['url'])
		if self.data.get_house(self.url):
			self.data.move(grandparent.url, house[0], house[1])
		else:
			self.data.build_house({'x':house[0],'y':house[1],'owner':self.name,'url':self.url})
		text += "\nYou now share a house!\n\n"
		text += "http://zatnosk.dk/playground/mastocity/?x={}&y={}".format(house[0],house[1])
		self._send_reply(text)

	def is_mine(self):
		return self.status['account']['acct'] == 'unrealestate'

	def dump(self):
		print("type: {}\nname: {}\nurl: {}\ntarget: {}\n{}\n".format(self.type, self.name, self.url, self.target, self._get_flat_content()))

	def _get_flat_content(self):
		if not self.content_flat:
			self.content_flat = re.sub('<.+?>','',self.status['content'])
		return self.content_flat

	def _parse_move(self):
		text = self._get_flat_content()
		target = self.re_move_target.search(text).group(1)
		matching_mentions = ()
		acct = None
		url = None
		for mention in self.status['mentions']:
			if target == mention['username']:
				matching_mentions += (mention,)
				if url == None:
					url = mention['url']
					acct = mention['acct']
		if len(matching_mentions) > 1:
			lowest_score = len(status['content'])
			for mention in matching_mentions:
				test = re.compile('move in with(.*?)'+mention['url'])
				match = test.search(status['content'])
				if match:
					score = len(match.group(1))
					if score > 0 and score < lowest_score:
						url = mention['url']
						acct = mention['acct']
						lowest_score = score
		if not acct and not url: return None
		else: return {'name':acct,'url':url}

	def _get_parent(self):
		if not self.parent and self.status['in_reply_to_id']:
			self.parent = Cache.get(self.status['in_reply_to_id'])
			if not self.parent:
				self._fetch_context()
				self.parent = Cache.get(self.status['in_reply_to_id'])
		return self.parent

	def _fetch_context(self):
		context = self.mastodon.status_context(self.status['id'])
		for status in context['ancestors']:
			NotifAnalyzer(status, self.mastodon, self.data)
		for cache in context['descendants']:
			NotifAnalyzer(status, self.mastodon, self.data)

	def _send_reply(self, text):
		self.mastodon.status_post(text, in_reply_to_id=self.status['id'], visibility=self.status['visibility'])

def catch_up(mastodon, data, max_id = None):
	state['mastodon'] = mastodon
	state['data'] = data
	bot = mastodon.account_verify_credentials()
	notifs = mastodon.notifications(max_id = None)
	waiting = []
	for notif in notifs:
		if notif['type'] != 'mention':
			continue
		is_handled = False
		context = mastodon.status_context(notif['status']['id'])
		for toot in context['descendants']:
			if toot['account']['acct'] == 'unrealestate':
				is_handled = True
				break
		if is_handled:
			break
		else:
			print("Queueing message from {}".format(notif['account']['acct']))
			waiting.append(notif)
	waiting.reverse()
	if len(waiting) == 0:
		print("No pending messages detected")
	else:
		print("Handling {} queued messages".format(len(waiting)))
	for notif in waiting:
		status = NotifAnalyzer(notif['status'],mastodon,data)
		status.analyse()
		status.reply()

admins = ("@zatnosk@manowar.social","@zatnosk@cybre.space")
def call_for_help(msg, reply_to=None):
	if(state['mastodon']):
		text = "Help me, Obi-Wan Kenobi, you're my only hope!\n["+msg+"]\n/cc"
		for admin in admins:
			text += " "+admin
		#state['mastodon'].status_post(text,visibility="direct")	
