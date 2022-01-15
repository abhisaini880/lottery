# Lottery service

1. This lottery service will accept the list of participants.
2. Breakdown the list into multiple parts as per regions.
3. Clean the data of each region
4. Assign lottery tickets as per sales data
5. Fetch the winners data for each region.

### Rules for alloting tickets

- Tickets will be alloted on the basis of sales done by participant.
- On sale of 20000, 1 ticket is alloted
- On sale of 30000, 2 ticket is alloted
- On sale of 50000, 5 ticket is alloted
- Max tickets that can be alloted to any participant is 15

### Rules for selecting winner

- Total number of winners to select is defined in config file.
- one participant with multiple tickets can only win max 3 times.

### How to run the lottery

1. Check if all the dependencies are installed.
    - Python3.x
    - python libs are mentioned in requirements.txt

2. Overwrite the basepath in `config.py` where you want the data to be stored.
3. Run `python3 start_lottery.py` - It will create the file system needed.
4. Then place the participants file in master folder.
5. Again run `python3 start_lottery.py`

> NOTE: Every time the lottery is started, it will create a new session for that

### Data location

- files for any region can be found under <basepath>/sessions/<region>

- Types of data recorded:
    1. participant file: It contains the data of all participants under that region.
    2. lottery file: It contains the data for all the tickets generated.
    3. winners file: It contains the data for all the tickets that wins the lottery from that region.
