import json
import os.path

def append_or_create_json_with_phrases_and_entities_fixed(phrases, markdown_files, json_cache_path):
    # Initialize or load existing JSON cache
    if os.path.exists(json_cache_path):
        with open(json_cache_path, 'r', encoding='utf-8') as f:
            phrases_and_entities = json.load(f)
        # Convert lists to sets for appending new entities
        for phrase, entities in phrases_and_entities.items():
            phrases_and_entities[phrase] = set(entities)
    else:
        phrases_and_entities = {}

    # Loop through all the markdown files to extract entities related to each phrase
    for md_file in markdown_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        cleaned_content = remove_html_tags(content)
        matches = square_bracket_combined_regex.findall(cleaned_content.lower())
        for match in matches:
            for phrase, entity in zip(phrases, match):
                if entity:
                    cleaned_entity = clean_up_text(entity.strip())
                    named_entity = extract_first_one_to_three_words(cleaned_entity)
                    if named_entity and len(named_entity.split()) <= 3 and len(named_entity) >= 3:
                        if phrase not in phrases_and_entities:
                            phrases_and_entities[phrase] = set()
                        phrases_and_entities[phrase].add(named_entity)

    # Convert sets back to lists for JSON serialization
    for phrase, entities in phrases_and_entities.items():
        phrases_and_entities[phrase] = list(entities)

    # Save the updated JSON object to the cache file
    with open(json_cache_path, 'w', encoding='utf-8') as f:
        json.dump(phrases_and_entities, f, ensure_ascii=False, indent=4)
      