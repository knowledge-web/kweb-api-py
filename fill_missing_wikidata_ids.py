
import json
import requests

def fetch_wikidata_id(entity_name):
    search_url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "format": "json",
        "language": "en",
        "search": entity_name
    }
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        search_results = response.json().get('search', [])
        if search_results:
            return search_results[0].get('id')
    return None

def fill_missing_wikidata_ids(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    updated_data = {}
    for phrase, entities in data.items():
        updated_entities = []
        for entity in entities:
            if not isinstance(entity, dict):
                entity_data = {'name': entity}
            else:
                entity_data = entity.copy()
            if 'wikidataId' not in entity_data:
                wikidata_id = fetch_wikidata_id(entity_data.get('name'))
                if wikidata_id:
                    entity_data['wikidataId'] = wikidata_id
            updated_entities.append(entity_data)
        updated_data[phrase] = updated_entities

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=4)

# Example usage
json_path = './.wikidata-name-search-cache.json'
fill_missing_wikidata_ids(json_path)
