import sys

# Class created to parse the touring output
class OptimalTouring():
	
	def __init__(self, given_file, input_file, verbose_flag):
		# Parse files
		self.parse_given_file(given_file)
		self.parse_input_file(input_file)
		# Initialize inputs
		self.verbose = verbose_flag
		self.prev_location = (0, 0)
		self.total_points = 0
		self.already_visited = []
		self.day = 0

	# Helper function to get the time in HH:MM format
	def get_time(self, minutes):
		full_time = minutes / 60.0
		just_hours = int(full_time)
		extra_minutes = str(int(60 * (full_time - just_hours)))
		just_hours_str = str(just_hours)
		if len(extra_minutes) == 1:
			extra_minutes = "0" + extra_minutes
		if len(just_hours_str) == 1:
			just_hours_str = "0" + just_hours_str
		return just_hours_str + ":" + extra_minutes

	# Function to parse the site file 
	def parse_given_file(self,given_file):
		# Names for columns in location file. Made for readability in lookup table
		location_file_names = ["ave", "st", "time", "pts"]
		# Names for used columns in day file. Made for readability in lookup table
		day_file_names = ["open", "close"]
		with open(given_file,"r") as f:
			lines = f.readlines()
			header_count = 0
			location_lookup = dict()
			hours_lookup = dict()
			for line in lines:
				data = line.split()
				if data == []:
					continue
				try:
					site_id = data[0]
					parsed_data = list(map(float,data[1:])) # Will return error if header line and increment the count
					if header_count == 0: # Error, first line should be a header
						raise ValueError("Input file is different, the first line should be a header and not information")
					elif header_count == 1: #we are in location file
						location_lookup[site_id] = dict(zip(location_file_names,parsed_data)) #add to lookup table
					else: # We are in open/close info part of the file
						dayval = int(parsed_data[0])
						# print("dayval: {}".format(dayval))
						hours_lookup.setdefault(dayval,{})
						hours_lookup[dayval][site_id] = list(map(lambda x: int(x) * 60, parsed_data[1:])) #add to lookup table and convert hours to minutes
				except:
					header_count += 1
		self.location_lookup = location_lookup
		self.hours_lookup = hours_lookup

	# Function to parse the output created by the team
	def parse_input_file(self,input_file):
		# Load algorithm info
		with open(input_file,"r") as f:
			lines = f.readlines()
			matrix = []
			for line in lines:
				separated = line.split() # split on whitespace
				matrix.append(separated)
			self.moves_by_day = matrix

	# Function to simulate visiting the sites based on the team's output file
	def play(self):
		# print(self.moves_by_day) -> check the sites visited on a day
		for locations in self.moves_by_day:
			self.day += 1 # since day starts at 1 in this game but enumerate starts at 0
			
			if not locations: continue
			
			curr_time = 0 # in minutes
			# if self.day > 3: break -> if input is in correct format should not need this statement
			current_hours_lookup = self.hours_lookup[self.day]

			if self.verbose:
				print("\nDAY", self.day)

			for i, curr_location in enumerate(locations):
				
				if self.verbose:
					print("\tThe time is now", self.get_time(curr_time))
				if curr_location in self.already_visited:
					if self.verbose:
						print("\t You have already gone to your next site, which is an illegal move. You do nothing for the rest of the day")
					# Not taken as loss
					break
				
				# Get info
				curr_info = self.location_lookup[curr_location]
				time_needed = curr_info["time"]
				points = curr_info["pts"]
				st = curr_info["st"]
				ave = curr_info["ave"]
				open_t,close_t = current_hours_lookup[curr_location]

				if i == 0:
					self.prev_location = (st, ave) # Start at first location each day
					dist = 0
				else:
					if self.verbose:
						print("\tGoing to location", i, "for the day: site", curr_location)
					dist = abs(st - self.prev_location[0]) + abs(ave - self.prev_location[1])
				
				if self.verbose:
					print("\tThe location is at", (st, ave), "and you are at", self.prev_location, "You must travel the distance of", dist, "units")
				curr_time += dist
				
				if int(self.get_time(curr_time).split(":")[0]) > 23:
					if self.verbose:
						print("\tThere is not enough time left in the day to get to the location you would like, skipping to the next day")
					break
				
				if self.verbose:
					print("\tThe time is now", self.get_time(curr_time), "and you have arrived at the site")
				
				if curr_time < open_t: #if place isnt open, wait until it's open
					if self.verbose:
						print("\tThis site is not open yet, We will wait until it is open")
					curr_time = open_t
					if self.verbose:
						print("\tThe time is now", self.get_time(curr_time), "and the site is open")
				
				if curr_time > close_t:
					if self.verbose:
						print("\tThe site is already closed or you don't have enough time to spent here. Wait until tomorrow.")
					# If already closed assume staying here rest of the day
					prev_location = (st,ave)
					break
				
				if curr_time + time_needed > close_t: 
					if self.verbose:
						print("\tYou don't have enough time until the site closes to spend the proper amount. Wait until tomorrow.")
					# If the amount of time you have to stay is too much since the place would close, 
					# assume staying for the rest of the day
					self.prev_location = (st, ave)
					break
				
				if curr_time >= open_t: # Place is now open and you can stay the correct amount of time
					if self.verbose:
						print("\tYou can now spend the amount of time you need here!", points, "points gained!")
					curr_time += time_needed
					self.total_points += points
					self.already_visited.append(curr_location)
					self.prev_location = (st, ave)

		if self.verbose:
			print("\nTotal Points:", round(self.total_points, 5))
		else:
			print("\tTotal Points:", round(self.total_points, 5))

# sys.argv[1] is the given file
# sys.stdin is the stdout of their algorithm as a file
verbose = False
if len(sys.argv) == 4:
	if sys.argv[3] == "-v":
		verbose = True
game = OptimalTouring(sys.argv[1], sys.argv[2], verbose)
game.play()

