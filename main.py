"""
Drop bad epochs by index from epoched MEG/EEG data.

This app removes specified epochs from an MNE Epochs object by their indices.
Epoch indices to drop can be provided either from a file or as a comma-separated
list in the configuration.

Inputs:
    - mne: Path to MNE epochs .fif file
    - events: Optional path to file containing comma-separated epoch indices to drop
    - drop: Optional comma-separated string of epoch indices to drop

Outputs:
    - out_dir/meg-epo.fif: Epochs file with specified epochs removed
    - out_dir/info.txt: Summary of dropped epochs
    - product.json: Metadata about dropped epochs
"""

# Copyright (c) 2026 brainlife.io
#
# Drop bad epochs from MNE epochs file by index.
#
# Authors:
# - Maximilien Chaumon (https://github.com/dnacombo)

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'brainlife_utils'))

# Standard imports
import re
import mne

# Import shared utilities
from brainlife_utils import (
    load_config,
    setup_matplotlib_backend,
    ensure_output_dirs,
    create_product_json,
    add_info_to_product
)

# Set up matplotlib for headless execution
setup_matplotlib_backend()

# Ensure output directories exist
ensure_output_dirs('out_dir')

# Load configuration
config = load_config()

# == LOAD DATA ==
data_file = config['mne']
epochs = mne.read_epochs(data_file, verbose=False)
print(f'Loaded {len(epochs)} epochs')

# == COLLECT INDICES TO DROP ==
todrop1 = []

# Read indices from file if provided
if config.get('events') and config['events'] != 'None':
    try:
        with open(config['events']) as f:
            todrop1 = f.read()
        # Turn todrop1 into a list of strings and remove leading/trailing whitespace
        todrop1 = todrop1.split(',')
        # Remove leading and trailing whitespace or commas in the list
        todrop1 = [re.sub(r'^\s*|\s*$', '', x) for x in todrop1]
        # Remove empty strings
        todrop1 = list(filter(None, todrop1))
        # Convert to integers
        todrop1 = [int(x) for x in todrop1]
        print(f'Read {len(todrop1)} epoch indices from file: {config["events"]}')
    except Exception as e:
        print(f'Warning: Could not read events file: {e}')
        todrop1 = []

# Parse drop parameter if provided
todrop2 = []
if config.get('drop') and config['drop'] != 'None':
    try:
        todrop2 = config['drop'].split(',')
        todrop2 = [int(x.strip()) for x in todrop2 if x.strip()]
        print(f'Read {len(todrop2)} epoch indices from config: {todrop2}')
    except Exception as e:
        print(f'Warning: Could not parse drop parameter: {e}')
        todrop2 = []

# Create union of todrop1 and todrop2 (remove duplicates)
todrop = sorted(list(set(todrop1) | set(todrop2)))

# == DROP EPOCHS ==
if todrop:
    print(f'Dropping {len(todrop)} epochs: {todrop}')
    epochs.drop(todrop)
    msg = f'Dropped {len(todrop)} epochs: {todrop}'
    add_info_to_product(msg)
else:
    print('No epochs to drop')
    add_info_to_product('No epochs dropped')

print(f'Remaining epochs: {len(epochs)}')

# == SAVE PROCESSED EPOCHS ==
epochs.save(os.path.join('out_dir', 'meg-epo.fif'), overwrite=True)

# == SAVE INFO TEXT FILE ==
info_text = f'Dropped epochs: {todrop}\nRemaining epochs: {len(epochs)}'
with open(os.path.join('out_dir', 'info.txt'), 'w') as f:
    f.write(info_text)

# == CREATE PRODUCT.JSON ==
create_product_json()
add_info_to_product(f'Total epochs dropped: {len(todrop)}', 'success')
