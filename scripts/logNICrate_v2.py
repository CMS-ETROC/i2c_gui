from bs4 import BeautifulSoup
import pandas as pd
import requests
# import schedule
import signal
import time
import argparse
import sqlite3
from pathlib import Path

channels = [f"{i}" for i in range(0,8)]

def convert_voltage(value):
    if 'V' in value:
        return float(value.replace(' V', '')) * 1
    elif 'mV' in value:
        return float(value.replace(' mV', '')) * 1e-3
    elif 'uV' in value:
        return float(value.replace(' uV', '')) * 1e-6
    return value

def read_single_data():
    url = requests.get('http://192.168.21.26/')
    soup = BeautifulSoup(url.content, 'html.parser')
    # timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    timestamp = pd.Timestamp.now().isoformat(sep=' ', timespec='seconds')

    #print(f'>> Log successful at {timestamp}')

    result = soup.find_all("body")[0]
    # Obtenemos todas las filas
    rows = result.find_all("tr")
    output_rows = []

    for row in rows:
        ### Check there are no errors ##
        #if 'Current too high' in str(row):
        #    bot_send_message(str(row), dont_send)

        if not any(ch in str(row) for ch in channels):
            continue
        # obtenemos todas las columns
        cells = row.find_all("td")
        output_row = []
        if len(cells) > 0:
            for cell in cells:
                output_row.append(cell.text)
            output_rows.append(output_row)

    #format_result = output_rows.text
    data = pd.DataFrame(output_rows)
    data.columns = ["Channel",
                    "Voltage",
                    "Current",
                    "Sense Voltage",
                    "Sense Current_uA",
                    "Terminal Voltage",
                    "Status"]

    data = data[["Channel",
                "Sense Voltage",
                "Sense Current_uA",
                "Terminal Voltage"]]

    data["timestamp"] = timestamp
    data = data[1:9]

    ### Surgery
    data['Channel'] = range(8)
    data['Channel'] = data['Channel'].astype('uint8')
    data['Sense Voltage'] = data['Sense Voltage'].apply(convert_voltage)
    data['Sense Voltage'] = data['Sense Voltage'].astype('float32')
    data['Terminal Voltage'] = data['Terminal Voltage'].apply(convert_voltage)
    data['Terminal Voltage'] = data['Terminal Voltage'].astype('float32')
    data['Sense Current_uA'] = data['Sense Current_uA'].str.replace(' uA', '', regex=False).astype(float)
    data['Sense Current_uA'] = data['Sense Current_uA'].astype('float32')

    outfile = outpath / 'HV_History.sqlite'
    with sqlite3.connect(outfile) as sqlconn:
        data.to_sql('hv', sqlconn, if_exists='append', index=False)


# def bot_send_message(bot_message, dont_send):
#     if dont_send: return
#     bot_token = api_key
#     bot_chatID = chat_id
#     send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
#     response = requests.get(send_text)
#     print(response)
#     dont_send = True

global exit_loop
exit_loop = False

if __name__=='__main__':
    parser = argparse.ArgumentParser(
                    prog='HV Logger',
                    description='Log output of DESY TB21 NI Crate HV',
                    )

    parser.add_argument(
        '-o',
        '--output-file',
        type = str,
        help = 'The name of the json file with HV vals. Default: "out" makes out.json',
        dest = 'output_file',
        default = 'out',
    )
    parser.add_argument(
        '-d',
        '--output-directory',
        type = Path,
        help = 'Path to where the json file should be stored. Default: ./',
        dest = 'output_directory',
        default = Path("./"),
    )

    parser.add_argument(
        '-t',
        '--time-limit',
        type = int,
        help = 'Amount of time to log for. Default: 5',
        dest = 'time_limit',
        default = 5,
    )

    args = parser.parse_args()

    outpath = Path(args.output_directory)
    # log_time = args.time_limit
    time_limit = args.time_limit

    #chat_id = "-4149555368" #Del grupo donde está el Bot
    #api_key = "7086061035:AAEslZSr3pPEsedeMFgWROmeBKuXljLfSzY"

    print('------------------- Start of run ---------------------')
    print(f'Output is saved to {outpath}')
    print(f'Will be logging for every {time_limit} seconds.')
    # start_time = time.time()


    # schedule.every(log_time).seconds.do(read_single_data)
    # while (time.time() - start_time) < time_limit:
    #     schedule.run_pending()


    def signal_handler(sig, frame):
        global exit_loop
        print("Exiting gracefully")
        exit_loop = True

    signal.signal(signal.SIGINT, signal_handler)

    while not exit_loop:
        read_single_data()
        time.sleep(args.time_limit)

    signal.pause()