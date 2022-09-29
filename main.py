import psycopg2

def create_db(conn):
    with conn.cursor() as cur:
        cur.execute("""
            DROP TABLE contacts;
            DROP TABLE clients;
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients(
                id SERIAL PRIMARY KEY,
                name VARCHAR(60),
                surname VARCHAR(60),
                email VARCHAR(50)
            );
        """)   
        cur.execute("""
            CREATE TABLE IF NOT EXISTS contacts(
                id SERIAL PRIMARY KEY,
                telephone VARCHAR(60),
                client_id INTEGER NOT NULL REFERENCES clients(id)
            );
        """)       
    conn.commit()             

def add_client(conn, first_name, last_name, email, phones=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO clients(name,surname,email) VALUES(%s,%s,%s) RETURNING id;
        """, (first_name, last_name, email))       
        client_id = cur.fetchone()[0]  
    if phones != None:
        add_phone(conn, client_id, phones)   

def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO contacts(telephone,client_id) VALUES(%s,%s);
        """, (phone, client_id))       
    conn.commit() 

def update_client(conn, client_id, first_name=None, last_name=None, email=None):
    fields = ''
    param = ()
    if first_name != None:
        fields+='name=%s,'
        param+=(first_name,)
    if last_name != None:
        fields+='surname=%s,'
        param+=(last_name,)
    if email != None:
        fields+='email=%s,'
        param+=(email,)
    
    fields = fields[0:len(fields)-1]
    param += (client_id,)

    text = """
            UPDATE clients SET {} WHERE id=%s;
        """.format(fields)

    with conn.cursor() as cur:
        cur.execute(text, (param))       
    conn.commit() 

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    pass

def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM contacts WHERE client_id=%s AND telephone=%s
        """, (client_id, phone))       
    conn.commit() 

def delete_client(conn, client_id):
    with conn.cursor() as cur:
        cur.execute("""
            DELETE FROM contacts WHERE client_id=%s 
        """, (client_id,))           
        cur.execute("""
            DELETE FROM clients WHERE id=%s 
        """, (client_id,))    
    conn.commit() 

def find_clientbyphone(conn, phone):
    with conn.cursor() as cur:
        cur.execute("""
                SELECT client_id FROM contacts WHERE telephone=%s
            """, (phone,))       
        return cur.fetchone()[0]     

def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    fields = ''
    param = ()
    if phone != None:
        client_id = find_clientbyphone(conn, phone)
        fields = 'id=%s'
        param = (client_id,)
    else:
        if first_name != None:
            fields+='name=%s AND '
            param+=(first_name,)
        if last_name != None:
            fields+='surname=%s AND '
            param+=(last_name,)
        if email != None:
            fields+='email=%s AND'
            param+=(email,)
        fields = fields[0:len(fields)-4]

    text = """
            SELECT * FROM clients WHERE {} ;
        """.format(fields)

    with conn.cursor() as cur:
        cur.execute(text, (param))       
        print(cur.fetchall()) 

with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as conn:
    # вызывайте функции здесь
    create_db(conn)
    add_client(conn, 'ivan', 'ivanov', 'ivan@,ail.ru', '+79829825858')
    add_phone(conn, 1, '+79829825859')
    update_client(conn, 1, first_name='Ivan', email='ivan@gmail.ru')
    find_client(conn, 'Ivan', email='ivan@gmail.ru')
    find_client(conn, phone='+79829825858')
    delete_phone(conn, 1, '+79829825859')
    delete_client(conn, 1)

conn.close()