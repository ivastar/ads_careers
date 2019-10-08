import glob
import numpy as np
import astropy
import astropy.io.ascii
import os
import urllib
import json
import yaml
from ads import gender
from ads import get_data
from ads import plot
ADS_KEY = os.getenv('ADS_KEY') 
GENDER_API_KEY = os.getenv('GENDER_API_KEY')
