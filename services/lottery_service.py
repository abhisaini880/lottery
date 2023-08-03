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
            "Region": "region",
            "Outlet Unique Code": "participant_id",
            "Mobile No.": "contact_number",
            "Coupons": "coupons_count",
            "Outlet Name": "participant_name",
        },
        inplace=True,
    )
    participants_data.dropna(
        subset=["region", "participant_id"],
        inplace=True,
    )
    participants_data["coupons_count"].fillna(0, inplace=True)

    # if isinstance(participants_data["sales"][0], str):
    #     participants_data["sales"] = participants_data["sales"].apply(
    #         lambda x: x.replace(",", "")
    #     )
    return


@DeprecationWarning
def number_of_lottery_coupons(total_sales):
    """
    Function to calculate the number of lottery
    coupons to assign for each participants based on sales.

    Args:
        total_sales(int): total sales done by the participant.
    """

    total_sales = int(total_sales)
    max_coupon_to_assign = 15

    sales_coupon_mapping = {20000: 1, 30000: 2, 50000: 5}

    sale_figures = list(sales_coupon_mapping.keys())
    coupon_count = 0

    while (
        total_sales and sale_figures and coupon_count <= max_coupon_to_assign
    ):
        sale = sale_figures.pop()
        if total_sales >= sale:
            remaining_sale = total_sales // sale
            total_sales %= sale
            coupon_count += remaining_sale * sales_coupon_mapping[sale]

    return min(coupon_count, max_coupon_to_assign)


@DeprecationWarning
def number_of_lottery_coupons_by_veet_units(veet_units):
    """
    Function to calculate the number of lottery
    coupons to assign for each participants based on veet units.

    Args:
        veet_units (int): count of veet units
    """
    veet_units = int(veet_units)

    max_coupon_to_assign = 15

    veet_coupon_mapping = {1: 1, 2: 3, 3: 5}

    veet_figures = list(veet_coupon_mapping.keys())
    coupon_count = 0

    while veet_units and veet_figures and coupon_count <= max_coupon_to_assign:
        veet_unit = veet_figures.pop()
        if veet_units >= veet_unit:
            remaining_sale = veet_units // veet_unit
            veet_units %= veet_unit
            coupon_count += remaining_sale * veet_coupon_mapping[veet_unit]

    return min(coupon_count, max_coupon_to_assign)


def generate_coupon(coupon_length):
    """
    Function to generate coupon ID
    * It will generate the coupon ID using alpha numeric characters
    * It uses `random` lib to select combination of characters

    Args:
        coupon_length(int): length of coupon characters
    """
    return "".join(random.choices(string.digits[1:], k=coupon_length))


def assign_lottery_coupons(participants_data, coupons_collection):
    """
    Function to assign lottery coupons to participants
    * It assigns the lottery coupon id as per the coupons assigned
        to each participant

    Args:
        participants_data(DataFrame): participants data for one region
    """
    coupon_mapping_df = pd.DataFrame(
        columns=[
            "participant_id",
            "region",
            "contact_number",
            "sales",
            "coupon_id",
        ]
    )
    coupon_length = 5

    for _, participant in participants_data.iterrows():
        count = 0
        while count < participant["coupons_count"]:
            coupon_id = generate_coupon(coupon_length)
            if (
                not coupon_mapping_df["coupon_id"].isin([coupon_id]).any()
                and coupon_id not in coupons_collection
            ):
                coupon_mapping_df = coupon_mapping_df.append(
                    {
                        "participant_id": participant["participant_id"],
                        "participant_name": participant["participant_name"],
                        "region": participant["region"],
                        "contact_number": participant["contact_number"],
                        "coupon_id": coupon_id,
                    },
                    ignore_index=True,
                )
                count += 1
                coupons_collection.append(coupon_id)

    return coupon_mapping_df, coupons_collection


def get_lottery_winners(lottery_data, winners_count):
    """
    Function call to fetch the lottery winners from
    lottery coupons.
    * First find out estimated winners from lottery data
        if estimated winners are less than expected winners than
        use estimated winners count
    * fetch the random winner, if fetched the coupon of existing winner with 3 winnings
        then discard that winner. Also, do not consider for fetching next winner.

    Args:
        lottery_data(DataFrame): Lottery coupons dataframe
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
    # lottery_grouped_data["counts"] = lottery_grouped_data["counts"].apply(
    #     lambda x: 3 if x > 3 else x
    # )
    max_coupons_can_win = lottery_grouped_data["counts"].sum()
    winners_count = min(max_coupons_can_win, winners_count)

    temp_winners_dict = defaultdict(int)
    winners_df = pd.DataFrame()
    winners_found = 0
    one_participant_winning_limit = 1
    temp_lottery_df = lottery_data.copy()

    while winners_found < winners_count:
        random_winner = temp_lottery_df.sample(n=1)
        participant_id = random_winner["participant_id"].iat[0]
        coupon_id = random_winner["coupon_id"].iat[0]

        if (
            temp_winners_dict.get(participant_id, 0)
            < one_participant_winning_limit
        ):
            winners_df = winners_df.append(random_winner)
            temp_winners_dict[participant_id] += 1
            winners_found += 1
            temp_lottery_df.drop(
                temp_lottery_df[
                    temp_lottery_df["coupon_id"] == coupon_id
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
    participant_file,
    region_list,
    config_data,
):
    """
    Main function call to orchestrate all other functions to fetch the
    winners list and store that list in seprate file.
    """
    coupons_collection = []
    for region in region_list:
        region_file_path = os.path.join(latest_session_path, region)
        lottery_file_path = os.path.join(region_file_path, lottery_file)
        participant_file_path = os.path.join(
            region_file_path, participant_file
        )
        total_winners_count = (
            config_data.get("winners_count", {}).get(region, {}).get("total")
        )

        # if not winner count then exit
        if not total_winners_count:
            continue

        # if file not found on filepath then exit
        if not os.path.isfile(participant_file_path):
            continue

        # read data from file
        participants_data = pd.read_csv(participant_file_path)

        # clean the participants file data
        clean_file_data(participants_data)

        # assign the number of lottery coupons to user
        # participants_data["coupons_count"] = participants_data["sales"].apply(
        #     lambda x: number_of_lottery_coupons(x)
        # )

        # participants_data["coupons_count"] = participants_data[
        #     "coupons_count"
        # ] + participants_data.apply(
        #     lambda x: number_of_lottery_coupons_by_veet_units(x.veet_units)
        #     if x.sales >= 20000
        #     else 0,
        #     axis=1,
        # )

        # generate the lottery coupons for user
        # create a seprate file for storing the lottery coupon id with user data
        coupons_data, coupons_collection = assign_lottery_coupons(
            participants_data, coupons_collection
        )

        # save the lottery data in a seperate file
        coupons_data.to_csv(lottery_file_path, index=False)

        # select the winners from the file - max 20
        # 1 user cannot win more than 3 times
        winners = get_lottery_winners(coupons_data, total_winners_count)

        start, end = 0, 0
        for prize, winners_count in (
            config_data.get("winners_count", {}).get(region, {}).items()
        ):
            if prize == "total":
                continue
            # save the winners data in a seperate file
            start = end
            end += winners_count
            winners_file_path = os.path.join(region_file_path, f"{prize}.csv")
            winners.iloc[start:end].to_csv(winners_file_path, index=False)


if __name__ == "__main__":
    pass
