import os

def get_api_key():
    
    api_key = os.environ.get('API_TOKEN_TELEWORDER')
    
    if api_key is None:
        raise Exception('API TOKEN is not provided')

    return api_key
     

def get_db_path():

    db_path = os.environ.get('DB_PATH')

    if db_path is None:
        raise Exception('Database`s path is not provided')

    return db_path