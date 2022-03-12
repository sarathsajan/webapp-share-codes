# Import Google Firebase libraries
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Initialise the Firebase firestore database using service account credentials
if not firebase_admin._apps:
    cred = credentials.Certificate('env_vars/fhsc-database-3ab0770b0616.json')
    default_app = firebase_admin.initialize_app(cred)
gcfsDB = firestore.client()


def set_user_data_gcfsDB(user_data):
    doc_ref = gcfsDB.collection('users').document(user_data['users_email'])
    doc_ref.set(
        {
            'unique_id': user_data['unique_id'],
            'users_name': user_data['users_name'],
            'users_email': user_data['users_email'],
            'picture': user_data['picture']
        }
    )


def if_user_data_exists_gcfsDB(user_data):
    doc_ref = gcfsDB.collection('users').document(user_data['users_email'])
    doc = doc_ref.get()
    if doc.exists:
        return True
    else:
        return False

def get_single_share_code_data(game, share_code):
    docs = gcfsDB.collection('share_codes').where('game', '==', game).where('share_code', '==', share_code).stream()
    results = []
    if docs:
        for item in docs:
            results.append(item.to_dict())
        print(results)
        return results
    return False

def check_and_add_share_code_gcfsDB(share_code_candidate):
    if get_single_share_code_data(share_code_candidate['game'], share_code_candidate['share_code']):
        return 'exists'
    else:
        doc_ref = gcfsDB.collection('share_codes')
        doc_ref.add(share_code_candidate)

def get_search_results():
    pass