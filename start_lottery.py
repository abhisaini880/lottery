""" Start the lottery process """

try:
    import os
    from json import load, dump
    from services import filter_service, lottery_service
except Exception as err:
    print(
        "Unable to access the python libraries. Please install the required libs from requirements.txt"
    )
    exit()

########
# INIT #
########
# First initialize the filesystem required for the lottery
print(
    "\n###############################################################################"
)
print(
    "#--------------------------- STARTING LOTTERY --------------------------------#"
)
print(
    "###############################################################################"
)
print("\n * checking the filesystem ")

# read config
config_file = "config.json"
if not os.path.isfile(config_file):
    print(
        "\n - Exiting: Config file not found. Please check the config file and try again.\n"
    )
    exit()

with open(config_file, "r") as config:
    config_data = load(config)

# if config data not found then then exit()
if not config_data:
    print(
        "\n - Exiting: Config data not found. Please check the config file and try again.\n"
    )
    exit()


base_path = config_data.get("base_path", os.getcwd())

if not os.path.isdir(base_path):
    print(
        "\n - Exiting: Base path not found. Please check the config file and try again.\n"
    )
    exit()

master_dir = os.path.join(base_path, config_data.get("master_path", "master"))
session_dir = os.path.join(
    base_path, config_data.get("session_path", "sessions")
)

# create the master and sessions directory if not present
if not os.path.isdir(master_dir):
    print("\n - Creating master directory ")
    os.mkdir(master_dir)

if not os.path.isdir(session_dir):
    print("\n - Creating sessions directory ")
    os.mkdir(session_dir)


master_filepath = os.path.join(
    base_path, master_dir, config_data.get("master_file", "master.csv")
)

# if master file not found then exit
if not os.path.isfile(master_filepath):
    print(
        "\n - Please place the participants data file in master dir with name"
        f" - `{config_data.get('master_file', 'master.csv')}`"
        " and run the lottery again.\n"
    )
    exit()

# fetch the next lottery session index
totalDir = 0
for base, dirs, files in os.walk(session_dir):
    if base != session_dir:
        continue
    for directories in dirs:
        totalDir += 1

session_index = config_data.get("session_index", totalDir + 1)
session_folder = f"session_{session_index}"

latest_session_dir = os.path.join(session_dir, session_folder)
os.mkdir(latest_session_dir)

config_data["session_index"] = session_index + 1
config_data["latest_session"] = session_folder

# write back the session index in config file
with open(config_file, "w") as config:
    dump(config_data, config)

#################
# Start Process #
#################

print("\n * Filtering the regions data from master file")
region_list = filter_service.main(
    master_file_path=master_filepath, lastest_session_path=latest_session_dir
)

print("\n * Running the lottery service")
lottery_service.main(
    latest_session_path=latest_session_dir,
    participant_file=config_data.get("participant_file", "participants.csv"),
    lottery_file=config_data.get("lottery_file", "lottery.csv"),
    winners_file=config_data.get("winners_file", "winners.csv"),
    region_list=region_list,
    config_data=config_data,
)

print("\n * Lottery services ended.")
print(
    f"\n * Winners list can be found in {config_data.get('winners_file', 'winners.csv')} inside latest session"
)

print(
    "\n###############################################################################"
)
print(
    "#------------------------------ Lottery Ended --------------------------------#"
)
print(
    "###############################################################################\n"
)
