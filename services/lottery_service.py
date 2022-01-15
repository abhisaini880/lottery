#!/usr/bin/env python
# coding: utf-8

# # Lottery service

# Import dependencies
import pandas as pd
import random
import string
import os
from collections import defaultdict


def clean_file_data(participants_data):
    """
    Function to clean the data
    * clean data for NAN values
    * replace , in price column
    * rename columns

    Args:
        participants_data(DataFrame): participants data for all clusters
    """
    participants_data.rename(
        columns={
            "Lucky Draw Cluster": "region",
            "Primary Key": "participant_id",
            "Total Sales": "sales",
            "KYC contact Number": "contact_number",
        },
        inplace=True,
    )
    participants_data.dropna(
        subset=["region", "participant_id", "sales", "contact_number"],
        inplace=True,
    )
    if isinstance(participants_data["sales"], str):
        participants_data["sales"] = participants_data["sales"].str.replace(
            ",", ""
        )
    return


def number_of_lottery_tickets(total_sales):
    """
    Function to calculate the number of lottery
    tickets to assign for each participants.

    Args:
        total_sales(int): total sales done by the participant.
    """

    total_sales = int(total_sales)
    max_ticket_to_assign = 15

    sales_ticket_mapping = {20000: 1, 30000: 2, 50000: 5}

    sale_figures = list(sales_ticket_mapping.keys())
    ticket_count = 0

    while (
        total_sales and sale_figures and ticket_count <= max_ticket_to_assign
    ):
        sale = sale_figures.pop()
        if total_sales >= sale:
            remaining_sale = total_sales // sale
            total_sales %= sale
            ticket_count += remaining_sale * sales_ticket_mapping[sale]

    return min(ticket_count, max_ticket_to_assign)


def generate_ticket(ticket_length):
    """
    Function to generate ticket ID
    * It will generate the ticket ID using alpha numeric characters
    * It uses `random` lib to select combination of characters

    Args:
        ticket_length(int): length of ticket characters
    """
    return "".join(
        random.choices(string.ascii_uppercase + string.digits, k=ticket_length)
    )


def assign_lottery_tickets(participants_data):
    """
    Function to assign lottery tickets to participants
    * It assigns the lottery ticket id as per the tickets assigned
        to each participant

    Args:
        participants_data(DataFrame): participants data for one region
    """
    ticket_mapping_df = pd.DataFrame(
        columns=[
            "participant_id",
            "region",
            "contact_number",
            "sales",
            "ticket_id",
        ]
    )
    ticket_length = 10

    for _, participant in participants_data.iterrows():
        count = 0
        while count < participant["tickets_count"]:
            ticket_id = generate_ticket(ticket_length)
            if not ticket_mapping_df["ticket_id"].isin([ticket_id]).any():
                ticket_mapping_df = ticket_mapping_df.append(
                    {
                        "participant_id": participant["participant_id"],
                        "region": participant["region"],
                        "contact_number": participant["contact_number"],
                        "sales": participant["sales"],
                        "ticket_id": ticket_id,
                    },
                    ignore_index=True,
                )
                count += 1

    return ticket_mapping_df


def get_lottery_winners(lottery_data, winners_count):
    """
    Function call to fetch the lottery winners from
    lottery tickets.
    * First find out estimated winners from lottery data
        if estimated winners are less than expected winners than
        use estimated winners count
    * fetch the random winner, if fetched the ticket of existing winner with 3 winnings
        then discard that winner. Also, do not consider for fetching next winner.

    Args:
        lottery_data(DataFrame): Lottery tickets dataframe
        winners_count(int): Required winners count
    """
    # In case the lottery count is less than winners count
    # then winners count will be equal to lottery count
    lottery_grouped_data = (
        lottery_data["participant_id"]
        .value_counts()
        .rename_axis("participant_id")
        .reset_index(name="counts")
    )
    lottery_grouped_data["counts"] = lottery_grouped_data["counts"].apply(
        lambda x: 3 if x > 3 else x
    )
    max_tickets_can_win = lottery_grouped_data["counts"].sum()
    winners_count = min(max_tickets_can_win, winners_count)

    temp_winners_dict = defaultdict(int)
    winners_df = pd.DataFrame()
    winners_found = 0
    one_participant_winning_limit = 3
    temp_lottery_df = lottery_data.copy()

    while winners_found < winners_count:
        random_winner = temp_lottery_df.sample(n=1)
        participant_id = random_winner["participant_id"].iat[0]
        ticket_id = random_winner["ticket_id"].iat[0]

        if (
            temp_winners_dict.get(participant_id, 0)
            < one_participant_winning_limit
        ):
            winners_df = winners_df.append(random_winner)
            temp_winners_dict[participant_id] += 1
            winners_found += 1
            temp_lottery_df.drop(
                temp_lottery_df[
                    temp_lottery_df["ticket_id"] == ticket_id
                ].index,
                inplace=True,
            )
        else:
            temp_lottery_df.drop(
                temp_lottery_df[
                    temp_lottery_df["participant_id"] == participant_id
                ].index,
                inplace=True,
            )

    return winners_df


def main(
    latest_session_path,
    lottery_file,
    winners_file,
    participant_file,
    region_list,
    config_data,
):
    """
    Main function call to orchestrate all other functions to fetch the
    winners list and store that list in seprate file.
    """

    for region in region_list:

        region_file_path = os.path.join(latest_session_path, region)
        lottery_file_path = os.path.join(region_file_path, lottery_file)
        winners_file_path = os.path.join(region_file_path, winners_file)
        participant_file_path = os.path.join(
            region_file_path, participant_file
        )
        winners_count = config_data.get("winners_count", 20)

        # if file not found on filepath then exit
        if not os.path.isfile(participant_file_path):
            continue

        # read data from file
        participants_data = pd.read_csv(participant_file_path)

        # clean the participants file data
        clean_file_data(participants_data)

        # assign the number of lottery tickets to user
        participants_data["tickets_count"] = participants_data["sales"].apply(
            lambda x: number_of_lottery_tickets(x)
        )

        # generate the lottery tickets for user
        # create a seprate file for storing the lottery ticket id with user data
        tickets_data = assign_lottery_tickets(participants_data)

        # save the lottery data in a seperate file
        tickets_data.to_csv(lottery_file_path)

        # select the winners from the file - max 20
        # 1 user cannot win more than 3 times
        winners = get_lottery_winners(tickets_data, winners_count)

        # save the winners data in a seperate file
        winners.to_csv(winners_file_path)


if __name__ == "__main__":
    pass
