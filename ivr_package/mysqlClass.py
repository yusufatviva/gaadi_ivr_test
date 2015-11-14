__author__ = 'shadow walker'
import pymysql
import pymysql.cursors


class MySQL:
	def __init__(self, DBHOST, DBPORT, DBUSER, DBPASSWD, DBNAME):
		self.conn = None
		try:
			self.conn = pymysql.connect(host=DBHOST, port=DBPORT, user=DBUSER, passwd=DBPASSWD, db=DBNAME,
			                            cursorclass=pymysql.cursors.DictCursor)
			self.conn.autocommit(1)
		except pymysql.DatabaseError as exc:
			print(exc)
			exit()

	def executeSQL(self, sql):
		temp = []
		count = 0
		result = {}
		cur = self.conn.cursor()
		try:

			cur.execute(sql)
			# for row in cur:
			# temp.append(row)
			# count += 1
			temp = cur.fetchall()
			# count = len(temp)
			count = cur.rowcount
			result['rows'] = temp
			result['count'] = count
			cur.close()

			return result
		except cur.DatabaseError as sql_exception:
			print(sql_exception)
			result['rows'] = temp
			return result

	def get_conn(self):
		return self.conn

	def escapeString(self, arg):
		return self.conn.escape_string(str(arg))

	def lastInsertId(self):
		return self.conn.insert_id()

	def afftectedRows(self):
		return self.conn.affected_rows()

	def destroy(self):
		self.conn.close()

	def get_connection(self):
		return self.conn.ping(True)
