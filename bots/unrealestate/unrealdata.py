import mysql.connector
from random import randint
from unrealmasto import call_for_help

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

class Data():
	def __init__(self):
		self.connection = mysql.connector.connect(**config)

	def cursor(self):
		try:
			return self.connection.cursor()
		except mysql.connector.errors.OperationalError:
			self.connection.close()
			self.connection = mysql.connector.connect(**config)
			try:
				return self.connection.cursor()
			except mysql.connector.errors.OperationalError:
				call_for_help('double mysql connection error')
				return None

	def get_house(self,url):
		cursor = self.cursor()
		select = "SELECT x,y,owner,url FROM houses WHERE url = %s LIMIT 1"
		cursor.execute(select,(url,))
		return cursor.fetchone()

	def get_residents(self,x,y):
		cursor = self.cursor()
		select = "SELECT owner,url FROM houses WHERE x = %s AND y = %s"
		cursor.execute(select,(x,y))
		return cursor

	def move(self,url,x,y):
		cursor = self.cursor()
		update = "UPDATE houses SET x=%s, y=%s, since=NOW() WHERE url = %s"
		cursor.execute(update,(x,y,url))
		self.connection.commit()

	def build_house(self,house):
		cursor = self.cursor()
		insert = ("INSERT INTO houses"
			" (x,y,owner,url)"
			" VALUES (%(x)s, %(y)s, %(owner)s, %(url)s)")
		cursor.execute(insert, house)
		self.connection.commit()

	def find_random_spot(self):
		d = randint(0,7)
		x = (d + 2) % 3 - 1
		y = (int(d/3) + 2) % 3 - 1
		select = ("SELECT a.x+%(x)s AS x,a.y+%(y)s AS y FROM houses AS a"
			" LEFT JOIN houses AS b ON a.x+%(x)s = b.x AND a.y+%(y)s= b.y"
			" WHERE b.owner IS NULL"
			" ORDER BY RAND() LIMIT 1")
		cursor = self.cursor()
		cursor.execute(select,{'x':x,'y':y})
		return cursor.fetchone()

	def get_bounds(self):
		cursor = self.cursor()
		select = ("SELECT MIN(x) AS minx, MAX(x) as maxx, MIN(y) AS miny, MAX(y) AS maxy"
			" FROM houses")
		cursor.execute(select)
		for (minx,maxx,miny,maxy) in cursor:
			return (minx,maxx,miny,maxy)

	def get_all(self):
		cursor = self.cursor()
		select = "SELECT * FROM houses"
		cursor.execute(select)
		for (x,y,owner,url) in cursor:
			print("{}, {}, {}, {}".format(x,y,owner,url))

	def show(self):
		cursor = self.cursor()
		cursor.execute("SHOW COLUMNS IN houses")
		for row in cursor:
			print(row)

	def post_status(self, status):
		author = status['account']['url']
		house = self.get_house(author)
		if house != None:
			x,y,_,_ = house
			select = "SELECT house_x, house_y, offset_x, offset_y, owner, locked\
				FROM posts\
				WHERE (house_x = %(x)s AND house_y = %(y)s)\
				OR (house_x = %(x)s+1 AND house_y = %(y)s AND offset_x)\
				OR (house_x = %(x)s AND house_y = %(y)s+1 AND offset_y)\
				OR (house_x = %(x)s+1 AND house_y = %(y)s+1 AND offset_x AND offset_y)"
