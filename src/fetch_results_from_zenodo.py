import json
from pathlib import Path
import urllib.request

ZENODO_RECORD_ID = 7422361

if __name__ == '__main__':
    # Get the list of all the files in the Zenodo repository
    # using pure urllib library
    url = 'https://zenodo.org/api/records/{}'.format(ZENODO_RECORD_ID)
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode('utf-8'))
        files = data['files']
        
        # check if topas.zip is in the list of files
        topas_results_filename = 'topas.zip'
        path_to_location_of_this_script = Path(__file__).parent.absolute()
        topas_results_dest_dir = Path(path_to_location_of_this_script.parent, 'data', 'topas', 'results')
        if topas_results_filename in (f['key'] for f in files):
            url = f'https://zenodo.org/record/{ZENODO_RECORD_ID}/files/{topas_results_filename}'
            # download the file into temporary directory
            path_to_temp_location = urllib.request.urlretrieve(url)
            print(path_to_temp_location)
            # unzip into `topas_results_dest_dir`
            import zipfile
            with zipfile.ZipFile(path_to_temp_location[0], 'r') as zip_ref:
                zip_ref.extractall(topas_results_dest_dir)

