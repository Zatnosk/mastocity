#!/usr/bin/python3
from mastodon import Mastodon
from unrealdata import Data
from unrealmasto import NotifListener, call_for_help, catch_up
import os

mastodon = Mastodon(
	client_id = os.path.dirname(os.path.abspath(__file__))+'/../secrets/mastobot_clientcred.secret',
	access_token = os.path.dirname(os.path.abspath(__file__))+'/../secrets/unreal_usercred.secret',
	api_base_url = 'https://manowar.social'
)

data = Data()
catch_up(mastodon, data)
listen = NotifListener(mastodon, data)
try:
	mastodon.user_stream(listen)
except:
	call_for_help('I\'m crashing!');
