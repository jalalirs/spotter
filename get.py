import json
from pysofar.sofar import SofarApi
from pysofar.spotter import Spotter
from datetime import datetime
from datetime import date, timedelta
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)


logger = logging.getLogger(__name__)

def dates_bwn_twodates(start_date, end_date):
	delta_days = int((end_date - start_date).days)
	return [(start_date + timedelta(n)).strftime("%Y-%m-%d") for n in range(delta_days)] + [end_date.strftime("%Y-%m-%d")]

def main():
	date_start = args.start
	date_end = args.end
	data_file = args.data
	data = None
	if not date_start and not data_file:
		logger.error("Couldn't determine start date")
		exit()
	elif not date_start:
		with open(data_file) as f:
			data = json.loads(f)
			date_start = datetime.strptime(data[-1]["date"])

	if not date_end:
		date_end = datetime.now()
	
	logger.info(f"Grabbing data from {date_start} {date_end}")

	api = SofarApi()
	spotters = api.get_spotters()
	logging.info(f"Spotters in account: {','.join([a.id for a in spotters])}")
	if args.spotter:
		spotters = [a for a in spotters if a.id in args.spotter.split(",")]
	
	dates = dates_bwn_twodates(date_start,date_end)
	spotter_oper_data = ['battery_power', 'battery_voltage', 'humidity', 'solar_voltage']
	spotter_data = {s.id:{k:[] for k in args.keys + spotter_oper_data} for s in spotters}
	logging.info(f"Grabbing data for: {','.join([a.id for a in spotters])}")

	start_str = date_start.strftime("%Y-%m-%d")
	end_str   = date_end.strftime("%Y-%m-%d")
	data = {"start": start_str,
		"end": end_str, 
		"data": spotter_data}
	
	filename = f"data/{start_str}_{end_str}.json"
	logging.info(f"Storing data in {filename}")

	for k in spotter_oper_data:
		for s in spotters:	
			spotter_data[s.id][k] = getattr(s,k)

	for i in range(1,len(dates)):
		for s in spotters:	
			logger.info(f"Grabbing data for {s.id} for dates {dates[i-1]} to {dates[i]}")
			d_date = s.grab_data(
				limit=500,
				start_date=dates[i-1],
				end_date=dates[i],
				include_surface_temp_data=True,
				include_waves= True, 
				include_wind = True,
				include_track = True, 
				include_frequency_data = True,
				include_directional_moments = True,
			)
			for k in args.keys:	
				spotter_data[s.id][k].append(d_date[k])
		# storing after each iteration to not repeat when fails
		with open(filename,"w") as f:
			f.write(json.dumps(data,indent=4))


if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Get data from sofarocean servers')
	parser.add_argument('--start', type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
		default=None, help='Date to start from (format: YYYY-MM-DD)')
	parser.add_argument('--end', type=lambda s: datetime.strptime(s, '%Y-%m-%d'),
		default=None, help='Date to end at (format: YYYY-MM-DD)')
	parser.add_argument('--data', type=str, default=None, help='If date not specified start from here')
	parser.add_argument('--spotter', type=str, default=None, help='Spotter id')
	parser.add_argument('--keys', type=lambda s: s.split(), 
		default="surfaceTemp waves frequencyData track wind", 
		help='Any combanation of the following keywords [surfaceTemp waves frequencyData track wind] seperated by space')

	args = parser.parse_args()
	main()
