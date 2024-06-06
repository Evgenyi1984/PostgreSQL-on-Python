import psycopg2

def create_db(conn):
	with conn.cursor() as cur:
		cur.execute("""
			DROP TABLE Phone;
			Drop Table Client;
		""")
		conn.commit()
		cur.execute("""
			CREATE TABLE IF NOT EXISTS Client(
			id SERIAL PRIMARY KEY,
			first_name VARCHAR(60) NOT NULL,
			last_name VARCHAR(60) NOT NULL,
			email VARCHAR(60) NOT NULL unique
		);
			""")
		conn.commit()

		cur.execute("""
			CREATE TABLE IF NOT EXISTS Phone(
			phones DECIMAL UNIQUE CHECK (phones <= 99999999999),
			id INTEGER REFERENCES Client(id));
			""")
		conn.commit()


def add_client (conn, first_name, last_name, email, phones=None):
	with conn.cursor() as cur:
		cur.execute("""
			INSERT INTO Client (first_name, last_name, email)
			VALUES ('%s', '%s' , '%s')
			RETURNING id;
			"""%(first_name, last_name, email))
		id_clients = cur.fetchone()[0]		    
		conn.commit()
		return id_clients
		


def add_phone (conn, id, phones):
	with conn.cursor() as cur:
		cur.execute("""
			INSERT INTO Phone (phones, id)
			VALUES ('%s', %s)
			RETURNING id;
			;
			"""%(phones, id))
		conn.commit()
	

def change_client(conn, id, first_name=None, last_name=None, email=None):
	with conn.cursor() as cur:
		cur.execute("""
			UPDATE Client
			SET first_name='%s', last_name='%s', email='%s'
			WHERE id=%s
			RETURNING id, first_name, last_name, email;
			""" %(first_name, last_name, email,id))
		conn.commit()
    
	

def change_phone(conn, id, old_phone, phones=None):
    with conn.cursor() as cur:
	    cur.execute("""
			UPDATE Phone
			SET phones='%s'
			WHERE id=%s and phones='%s'
			RETURNING id, phones;
			""" %(phones, id, old_phone))
	    
    

def delete_phone (conn, id, phones):
	with conn.cursor() as cur:
		cur.execute("""
			DELETE FROM Phone
			WHERE id=%s and phones='%s';
			""" %(id, phones))
	conn.commit()

def delete_client (conn, id):
	with conn.cursor() as cur:
		cur.execute("""
			DELETE FROM Client
			WHERE id=%s;
			""", (id,))
	conn.commit()

def find_client (conn, first_name=None, last_name=None, email=None, phones=None):
	with conn.cursor() as cur:
		cur.execute("""
			SELECT c.first_name, c.last_name, c.email, p.phones From Client c
			LEFT JOIN Phone p ON c.id = p.id
			WHERE c.first_name='%s' OR c.last_name='%s' OR c.email='%s' OR p.phones=%s;
			""" %(first_name, last_name, email, phones))
		return cur.fetchone()

conn = psycopg2.connect(database="clients_db", user= "postgres", password= "postgres") 
create_db(conn)
id_clients = add_client(conn,'Robert', 'Kron', 'Kron@yandex.ru')
print (id_clients)
print (add_phone(conn, id_clients, '89283567255'))
print (change_phone(conn, id_clients,'89283567255','89158645232'))
print (change_client (conn, id_clients, 'Nikolai', 'Ivanov', 'ivanov@gmail.com'))
print (delete_phone (conn, id_clients, '89158645232'))
print (find_client(conn, 'Nikolai',phones='89158645232'))
print (delete_client(conn, id_clients))

conn.close()