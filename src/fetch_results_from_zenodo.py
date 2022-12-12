import json
import urllib.request
import zipfile
from pathlib import Path

ZENODO_RECORD_ID = 7422361

files_and_dest_paths = {
    'topas.zip': 'data/topas/results',
    'shieldhit.zip': 'data/sh12a/results'
}

if __name__ == '__main__':

    # Get the list of all the files in the Zenodo repository using pure urllib library
    url = 'https://zenodo.org/api/records/{}'.format(ZENODO_RECORD_ID)
    print(f"Fetching the list of files from Zenodo repository: {url}")
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode('utf-8'))
        files = data['files']

        for results_filename, results_dest_dir in files_and_dest_paths.items():
            print(f"Checking if {results_filename} is in the list of files")
            # check if topas.zip is in the list of files
            if results_filename in (f['key'] for f in files):
                url = f'https://zenodo.org/record/{ZENODO_RECORD_ID}/files/{results_filename}'
                # download the file into temporary directory
                path_to_temp_location = urllib.request.urlretrieve(url)
                print(
                    f"Downloaded {results_filename} to {path_to_temp_location[0]}"
                )
                unpacking_dir = Path(
                    Path(__file__).parent.absolute(), results_dest_dir)
                with zipfile.ZipFile(path_to_temp_location[0], 'r') as zip_ref:
                    print(f"Unpacking {results_filename} to {unpacking_dir}")
                    zip_ref.extractall(unpacking_dir)
