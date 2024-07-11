import psycopg2

def create_db(conn):
	with conn.cursor() as cur:
		cur.execute("""
			DROP TABLE IF EXISTS Phone;
			Drop Table IF EXISTS Client;
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
	

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    cur = conn.cursor()
    query = "UPDATE client SET "
    if first_name:
        query += "first_name = %s, "
    if last_name:
        query += "last_name = %s, "
    if email:
        query += "email = %s, "
    query = query.rstrip(', ') + " WHERE id = %s"
    cur.execute(query, (first_name, last_name, email, client_id))
    if phones:
        cur.execute("DELETE FROM phones WHERE client_id = %s", (client_id,))
        for phone in phones:
            add_phone(conn, client_id, phone)
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

def find_client(conn, first_name=None, last_name=None, email=None, phones=None):
    cur = conn.cursor()
    query = "SELECT c.id, c.first_name, c.last_name, c.email, p.phones FROM Client c LEFT JOIN phone p ON c.id = p.id WHERE "
    if first_name:
        query += "c.first_name = %s AND "
    if last_name:
        query += "c.last_name = %s AND "
    if email:
        query += "c.email = %s AND "
    if phones:
        query += "p.phones = %s AND "
    query = query.rstrip(' AND ') + " ORDER BY c.id"
  
    cur.execute(query, (first_name, phones))
    return cur.fetchall()


if __name__ == "__main__":
	with psycopg2.connect(database="clients_db11", user= "postgres", password= "postgres")as conn: 
		create_db(conn)
		id_clients = add_client(conn,'Robert', 'Kron', 'Kron@yandex.ru')
		print (id_clients)
		print (add_phone(conn, id_clients, '89283567255'))
		print (change_phone(conn, id_clients,'89283567255','89158645232'))
		print (change_client (conn, id_clients, 'Nikolai', 'Ivanov', 'ivanov@gmail.com'))
		print (find_client(conn, 'Nikolai',phones='89158645232'))
		print (delete_phone (conn, id_clients, '89158645232'))
		print (delete_client(conn, id_clients))
