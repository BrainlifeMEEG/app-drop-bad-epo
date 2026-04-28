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
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'brainlife_utils'))
# Standard imports
import re
import numpy as np
import mne
# Import shared utilities
from brainlife_utils import (
    load_config,
    setup_matplotlib_backend,
    ensure_output_dirs,
    create_product_json,
    add_info_to_product,
    add_image_to_product
)
setup_matplotlib_backend()
# Ensure output directories exist
ensure_output_dirs('out_dir', 'out_report')
# Load configuration
config = load_config()
# == LOAD DATA ==
data_file = config['mne']
epochs = mne.read_epochs(data_file, verbose=False)
print(f'Loaded {len(epochs)} epochs')

# == VERIFICATION: log epoch count vs drop_log ==
n_current = len(epochs)
n_droplog = len(epochs.drop_log)
print(f'Current epoch count: {n_current}')
print(f'Drop log length (original count): {n_droplog}')
if n_current != n_droplog:
    print(f'NOTE: {n_droplog - n_current} epochs were previously dropped and are tracked in drop_log')

# == CREATE REPORT ==
report = mne.Report(title='Drop Bad Epochs Report')
report.add_epochs(epochs=epochs, title='Original Epochs before Dropping')
product_items = []
# get already discarded bad epochs for info
all_reasons = set(reason[0] for reason in epochs.drop_log if reason)
already_bad = [int(idx) for idx, reason in enumerate(epochs.drop_log) if reason]
if already_bad:
    print(f'Previously, {all_reasons} epochs were already dropped.')
    add_info_to_product(product_items, f'Previously dropped epochs {all_reasons}', 'info')

# == COLLECT INDICES TO DROP ==
todrop1 = []
# Read indices from file if provided
if config.get('events') and config['events'] != 'None':
    try:
        with open(config['events']) as f:
            todrop1 = f.read()
        todrop1 = todrop1.split(',')
        todrop1 = [re.sub(r'^\s*|\s*$', '', x) for x in todrop1]
        todrop1 = list(filter(None, todrop1))
        todrop1 = [int(x) for x in todrop1]
        print(f'Read {len(todrop1)} epoch indices from file: {config["events"]}')
        add_info_to_product(product_items, f'Read {len(todrop1)} epoch indices from file: {config["events"]}', 'info')
        todrop_epochs = epochs[todrop1]
        fig = todrop_epochs.plot_image(picks='data', combine='gfp', show=False)
        fig[0].savefig(os.path.join('out_dir', 'epochs_dropped_from_file.png'))
        plt.close(fig[0])
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
        add_info_to_product(product_items, f'Read {len(todrop2)} epoch indices from user input: {todrop2}', 'info')
        todrop_epochs = epochs[todrop2]
        fig = todrop_epochs.plot_image(picks='data', combine='gfp', show=False)
        fig[0].savefig(os.path.join('out_dir', 'epochs_dropped_from_config.png'))
        plt.close(fig[0])
    except Exception as e:
        print(f'Warning: Could not parse drop parameter: {e}')
        todrop2 = []

# Create union of all drops
todrop = sorted(list(set(todrop1) | set(todrop2)))

# == VERIFICATION: log event info for epochs being dropped ==
if todrop:
    print('\n=== VERIFICATION: Event info for epochs to be dropped ===')
    verification_lines = ['index, event_id, sample, condition']
    for idx in todrop:
        if idx < len(epochs):
            ev = epochs[idx].events[0]  # [sample, prev_id, event_id]
            try:
                cond = list(epochs[idx].event_id.keys())[0]
            except Exception:
                cond = 'unknown'
            line = f'{idx}, {ev[2]}, {ev[0]}, {cond}'
            print(line)
            verification_lines.append(line)
        else:
            msg = f'WARNING: index {idx} out of range (only {len(epochs)} epochs available)'
            print(msg)
            verification_lines.append(msg)
            add_info_to_product(product_items, msg, 'warning')

    # Save verification to file
    with open(os.path.join('out_dir', 'dropped_epochs_verification.txt'), 'w') as f:
        f.write('\n'.join(verification_lines))
    print('=== END VERIFICATION ===\n')

# plot epochs before dropping
fig = epochs.plot_image(picks='data', combine='gfp', show=False)
fig[0].savefig(os.path.join('out_dir', 'epochs_before_dropping.png'))
plt.close(fig[0])

# == DROP EPOCHS ==
if todrop:
    todrop_epochs = epochs[todrop]
    report.add_epochs(epochs=todrop_epochs, title='Dropped Epochs')
    print(f'Dropping {len(todrop)} epochs: {todrop}')
    epochs.drop(todrop)
    fig = epochs.plot_image(picks='data', combine='gfp', show=False)
    fig[0].savefig(os.path.join('out_dir', 'epochs_after_dropping.png'))
    plt.close(fig[0])
    msg = f'Dropped {len(todrop)} epochs: {todrop}'
    add_info_to_product(product_items, msg)
else:
    print('No epochs to drop')
    add_info_to_product(product_items, 'No epochs dropped')

print(f'Remaining epochs: {len(epochs)}')
print(f'Current epoch count: {len(epochs)}')
print(f'Drop log length: {len(epochs.drop_log)}')

# == SAVE PROCESSED EPOCHS ==
epochs.save(os.path.join('out_dir', 'meg-epo.fif'), overwrite=True)

# == SAVE INFO TEXT FILE ==
info_text = f'Dropped epochs: {todrop}\nRemaining epochs: {len(epochs)}'
with open(os.path.join('out_dir', 'info.txt'), 'w') as f:
    f.write(info_text)

# Add epochs visualization
report.add_epochs(epochs=epochs, title='Remaining Epochs After Dropping')

# Add drop statistics
report.add_html(
    title='Drop Summary',
    html=f'<div>'
         f'Total epochs dropped: {len(todrop)}<br>'
         f'Remaining epochs: {len(epochs)}<br>'
         f'Dropped indices: {todrop}'
         f'</div>'
)

# Save report
report.save(os.path.join('out_report', 'report.html'), overwrite=True)

# == CREATE PRODUCT.JSON ==
add_info_to_product(product_items, f'Total epochs dropped: {len(todrop)}', 'success')
add_image_to_product(product_items, name='Epochs before dropping', filepath=os.path.join('out_dir', 'epochs_before_dropping.png'))
if todrop:
    add_image_to_product(product_items, name='Epochs after dropping', filepath=os.path.join('out_dir', 'epochs_after_dropping.png'))
create_product_json(product_items)
