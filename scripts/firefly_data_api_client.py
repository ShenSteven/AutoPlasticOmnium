#!/usr/bin/env python
# coding: utf-8
"""
@File   : data_api.py
@Author : Steven.Shen
@Date   : 2021/9/10
@Desc   : 
"""
import argparse
import requests
import sys

local_url = "http://luxxxx:bento@localhost:8101/api/1/"
rs_url = "http://luxxxx:bento@10.90.104.16:8101/api/1/"  # SF results server IP. Most testings occur in SF
base_url = ""


# https://docs.google.com/document/d/1iiESDdm2Qhd8-rcwDn8C8FKgLZc09mBXnvwxsoJSRzU/edit

def check_connection():
    # will return "Connected" if the server is running
    url = base_url + "ping"
    response = requests.get(url)
    print(response.status_code)
    print(response.text)
    if "Connected" in response.text:
        return True


def post(results, endpoint="results", files=None):
    # will send the data to the server to be validated, but not saved
    # to save the values, this will need to be updated to endpoint="results"
    url = base_url + "firefly/" + endpoint
    data = {"run_results": results}
    response = requests.post(url, data=data, files=files)
    print("Result:%s" % response.status_code)
    print(response.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("simulated firefly data api client")
    parser.add_argument("-x", "--local", action="store_true", help="run against a localhost api instance")
    parser.add_argument("-s", "--station", action="append", help="station test_name")
    parser.add_argument("-f", "--file", action="append", help="Json FilePath")
    parser.add_argument("-l", "--log", action="append", help="test log")

    args = parser.parse_args()
    print(args)
    if args.local:
        print("local post:")
        base_url = local_url
    else:
        base_url = rs_url

    if not check_connection():
        sys.exit("Cannot connect to server")

    Post_json = open(args.file[0], "r").read()
    test_log = open(args.log[0], "r").read()

    print("%s post:" % args.station[0])
    if args.station[0] == "MBFT":
        litepoint = open("./Data/litepoint.zip", "rb").read()
        post(Post_json, files={"txt_log": test_log, "mbft_litepoint.zip": litepoint})
    elif args.station[0] == "SRF":
        litepoint = open("./Data/litepoint.zip", "rb").read()
        post(Post_json, files={"txt_log": test_log, "srf_litepoint.zip": litepoint})
    else:
        post(Post_json, files={"txt_log": test_log})
