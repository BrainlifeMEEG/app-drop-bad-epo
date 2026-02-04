# app-drop-bad-epo

[![Abcdspec-compliant](https://img.shields.io/badge/ABCD_Spec-v1.1-green.svg)](https://github.com/brain-life/abcd-spec)

## Description

Drops (rejects) bad epochs from MNE Epochs files by their indices using MNE-Python's [Epochs.drop()](https://mne.tools/stable/generated/mne.Epochs.html#mne.Epochs.drop) method. This app is useful for:
- Removing epochs marked as artifacts or bad quality
- Removing epochs by index from a separate quality control analysis
- Cleaning up epoched data for subsequent analysis

## Inputs

- **mne**: MNE epochs file in `.fif` format

## Outputs

- **out_dir/meg-epo.fif**: Epochs file with bad epochs removed
- **out_dir/info.txt**: Summary of dropped epochs
- **product.json**: Metadata with epoch information

## Configuration Parameters

### Required

- **mne**: Path to the input MNE epochs file (`.fif` format)

### Optional

- **drop**: Comma-separated list of epoch indices to drop (e.g., `"1, 25, 32"`)
- **events**: Path to a file containing epoch indices to drop (one per line or comma-separated)

Example configuration:
```json
{
    "mne": "path/to/epochs.fif",
    "drop": "1, 25, 32"
}
```

## Usage

The app reads an MNE epochs file and drops the specified epochs by their indices. Indices can be provided either directly via the `drop` parameter or read from a file specified in the `events` parameter. If both are provided, the union of both sets of indices is used.

## Technical Details

- **Execution**: Python with MNE-Python and shared brainlife_utils library
- **Data format**: MNE `.fif` format (compatible with all downstream Brainlife.io apps)
- **Epoch dropping**: Uses MNE's `Epochs.drop()` method for reliable epoch removal
- **Index handling**: Supports comma-separated indices or file-based index lists

## Authors

- [Maximilien Chaumon](https://github.com/dnacombo), Paris Brain Institute

## Citations

We kindly ask that you cite the following articles when publishing papers and code using this app:

**brainlife.io: A decentralized and open source cloud platform to support neuroscience research**. Hayashi, S., Caron, B. A., et al. & Pestilli, F. (2023). ArXiv. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10274934/

**MEG and EEG data analysis with MNE-Python**. Gramfort A, et al. & Hämäläinen MS. (2013). Frontiers in Neuroscience, 7(267):1–13. https://doi.org/10.3389/fnins.2013.00267

## Funding Acknowledgement

brainlife.io is publicly funded and for the sustainability of the project we kindly ask that you acknowledge the following funding sources:

[![NSF-BCS-1734853](https://img.shields.io/badge/NSF_BCS-1734853-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1734853)
[![NSF-BCS-1636893](https://img.shields.io/badge/NSF_BCS-1636893-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1636893)
[![NSF-ACI-1916518](https://img.shields.io/badge/NSF_ACI-1916518-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1916518)
[![NSF-IIS-1912270](https://img.shields.io/badge/NSF_IIS-1912270-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1912270)
[![NIH-NIBIB-R01EB030896](https://img.shields.io/badge/NIH_NIBIB-R01EB030896-green.svg)](https://grantome.com/grant/NIH/R01-EB030896-01)

#### MIT Copyright (c) 2026 brainlife.io The University of Texas at Austin and Indiana University

