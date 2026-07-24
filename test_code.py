def get_user(id):
    query = f"SELECT * FROM users WHERE id = {id}"
    result = db.execute(query)
    return {
        'id': result['id'],
        'password': result['password']
    }

def calculate(x, y):
    return x/y
