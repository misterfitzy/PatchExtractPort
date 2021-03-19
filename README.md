# PatchExtractPort
Python port of patching utility created by Greg Linares (@laughing_mantis). Greg did all the work I just ported it.

## Usage notes

This was ported to python3 to test it on a Mac. It uses 'cabextract' instead of expand.exe to work with the .cab files.

Steps:
- brew install cabextract
- python3 extracta-patch.py --patch windows10.0-kb4565351-x64_e4f46f54ab78b4dd2dcef193ed573737661e5a10.msu --path msu_dump

Note: all the extracted files will be stored under the folder specified by the --path option. You'll have to create that directory first.

See the help by running:
- python3 extracta-patch.py -h 


