from pathlib import Path
from astropy.nddata import CCDData
from astropy.io import fits
from astropy import wcs

def clean_header(path_to_file):
    """Clean the header from the keywords that trigger dss-specific errors in wcslib. Must be ran first on any opened image."""
    # DSS keywords that trigger errors in wcslib : XPIXELSZ, XPIXSZ, YPIXELSZ, YPIXSZ if they are in the header
    with fits.open(path_to_file, mode='update') as hdul:
        for keyword in ['XPIXELSZ', 'XPIXSZ', 'YPIXELSZ', 'YPIXSZ']:
            if keyword in hdul[0].header:
                del hdul[0].header[keyword]
        # Get the wcs and update the header with the fixed wcs
        w = wcs.WCS(hdul[0].header)
        hdul[0].header.update(w.to_header())
        # Remove duplicate keywords
        heaadhdu = hdul[0].header
        updated_dict = {}
        for key, value, comment in heaadhdu.cards:
            if key not in updated_dict:
                updated_dict[key] = (value, comment)
            else:
                if updated_dict[key] == (value, comment):
                    continue
                elif key == "DATE" : # Keep the most precise date : 
                    if len(value) > len(updated_dict[key][0]):
                        updated_dict[key] = (value, comment)
                elif (key == "CCD-TEMP") and (value == updated_dict[key][0]):
                    continue
                else:
                    raise ValueError(f"Duplicate keyword {key} found in header, with different values {value} and {updated_dict[key][0]}")
        new_head = fits.Header()
        for key, value in updated_dict.items():
            new_head[key] = value
        hdul[0].header = new_head
        hdul.flush()
        
