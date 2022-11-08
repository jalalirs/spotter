import pandas as pd
import glob
import json
import os
from pysofar.sofar import SofarApi
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

basedir = os.path.abspath(os.path.dirname(__file__))

def main():
	api = SofarApi()
	SPOTTERS = api.get_spotters()
	logging.info(f"Spotters in account: {','.join([a.id for a in SPOTTERS])}")
	datafiles = glob.glob(f"{basedir}/data/*.json")
	
	for s in SPOTTERS:
		data = {}
		sid = s.id
		for fname in sorted(datafiles):
			with open(fname) as f:
				seg_data = json.load(f)
				if sid not in seg_data["data"]:
					logging.info(f"no data for {sid} in {fname}")
					continue
				spot_data = seg_data["data"][sid]
				for k,v in spot_data.items():
					if k not in data:
						data[k] = []
					# loop over days
					if type(v) == float or type(v) == int:
						data[k].append(v)
					elif type(v) == list:
						for d_data in v:
							data[k] += d_data
		dfs = {k:pd.DataFrame(v) for k,v in data.items()}
		for k,df in dfs.items():
			df.to_csv(f"{basedir}/data/{sid}_{k}.csv",index=False)
			

if __name__ == '__main__':
	main()
