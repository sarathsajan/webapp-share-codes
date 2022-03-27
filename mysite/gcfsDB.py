# Import Google Firebase libraries
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from datetime import datetime, timedelta, timezone

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
            'picture': user_data['picture'],
            'account_creation_timestamp': datetime.now(timezone.utc),
            'last_upload_timestamp': datetime.now(timezone.utc) - timedelta(hours=24)
        }
    )


def if_user_data_exists_gcfsDB(user_data):
    doc_ref = gcfsDB.collection('users').document(user_data['users_email'])
    doc = doc_ref.get()
    if doc.exists:
        return True
    else:
        return False


def check_and_add_share_code_gcfsDB(share_code_candidate):
    upload_time_diff = 0
    doc = gcfsDB.collection('users').document(share_code_candidate['author_email']).get()
    doc = doc.to_dict()
    upload_time_diff = datetime.now(timezone.utc).astimezone() - doc['last_upload_timestamp']
    print(type(upload_time_diff))

    if get_single_share_code_data(share_code_candidate['game'], share_code_candidate['share_code']):
        return 'exists', upload_time_diff

    if upload_time_diff.days < 1:
        return 'not exists', upload_time_diff
    
    else:        
        doc_ref = gcfsDB.collection('share_codes')
        doc_ref.add(share_code_candidate)

        doc_ref = gcfsDB.collection('users').document(share_code_candidate['author_email'])
        doc_ref.update(
            {
                'last_upload_timestamp': datetime.now(timezone.utc)
            }
        )
        return 'not exists', upload_time_diff


def get_single_share_code_data(game, share_code):
    docs = gcfsDB.collection('share_codes')\
        .where('game', '==', game)\
        .where('share_code', '==', share_code)\
        .stream()
    results = []
    if docs:
        for item in docs:
            results.append(item.to_dict())
        return results
    return False


def get_search_results(search_query):
    def description_score(description_tokens, result_candidate):
        results = []
        for result in result_candidate:
            description_score = 0
            for token in description_tokens:
                if result['description'].find(token) != -1:
                    description_score = description_score + 1
            result['description_score'] = description_score
            results.append(result)
        return results
    
    if search_query['share_code_type'] == 'vinyl_group':
        docs = gcfsDB.collection('share_codes')\
                .where('game', '==', search_query['game'])\
                .where('share_code_type', '==', search_query['share_code_type'])\
                .stream()
    
    if search_query['share_code_type'] == 'livery_design':
        docs = gcfsDB.collection('share_codes')\
                .where('game', '==', search_query['game'])\
                .where('share_code_type', '==', search_query['share_code_type'])\
                .stream()
    
    if search_query['share_code_type'] == 'event_lab' and search_query['event_lab_season'] == 'all' and search_query['event_lab_racing_series'] == 'all':
        docs = gcfsDB.collection('share_codes')\
                .where('game', '==', search_query['game'])\
                .where('share_code_type', '==', search_query['share_code_type'])\
                .stream()

    if search_query['share_code_type'] == 'event_lab' and search_query['event_lab_season'] != 'all' and search_query['event_lab_racing_series'] == 'all':
        docs = gcfsDB.collection('share_codes')\
                .where('game', '==', search_query['game'])\
                .where('share_code_type', '==', search_query['share_code_type'])\
                .where('event_lab_season', '==', search_query['event_lab_season'])\
                .stream()

    if search_query['share_code_type'] == 'event_lab' and search_query['event_lab_season'] == 'all' and search_query['event_lab_racing_series'] != 'all':
        docs = gcfsDB.collection('share_codes')\
                .where('game', '==', search_query['game'])\
                .where('share_code_type', '==', search_query['share_code_type'])\
                .where('event_lab_racing_series', '==', search_query['event_lab_racing_series'])\
                .stream()

    if search_query['share_code_type'] == 'event_lab' and search_query['event_lab_season'] != 'all' and search_query['event_lab_racing_series'] != 'all':
        docs = gcfsDB.collection('share_codes')\
                .where('game', '==', search_query['game'])\
                .where('share_code_type', '==', search_query['share_code_type'])\
                .where('event_lab_season', '==', search_query['event_lab_season'])\
                .where('event_lab_racing_series', '==', search_query['event_lab_racing_series'])\
                .stream()

    results_candidate = []
    if docs:
        for item in docs:
            results_candidate.append(item.to_dict())
        results = description_score(search_query['search_description'], results_candidate)
        return results
    return False

def get_user_submitted_share_codes(author_email):
    doc_ref = gcfsDB.collection('share_codes')
    docs = doc_ref.where('author_email', '==', author_email).stream()
    results = []
    if docs:
        for item in docs:
            results.append(item.to_dict())
        return results
    return False