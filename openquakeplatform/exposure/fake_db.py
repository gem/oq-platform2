import os
def gem_fake_db_get(name): 
    script_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(script_dir, 'fake_data', name)
    with open(abs_file_path, 'r') as f:
        return f.read()

