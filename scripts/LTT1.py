LTT1 = '[' \
       '    {' \
       '        "myWind": null,' \
       '        "logger": null,' \
       '        "name": "WA580-Open",' \
       '        "_index": 1,' \
       '        "isTest": true,' \
       '        "suiteResult": true,' \
       '        "isTestFinished": false,' \
       '        "totalNumber": 2,' \
       '        "suiteVar": "",' \
       '        "steps": [' \
       '            {' \
       '                "myWind": null,' \
       '                "logger": null,' \
       '                "breakpoint": false,' \
       '                "suiteIndex": 0,' \
       '                "_index": 0,' \
       '                "testValue": null,' \
       '                "start_time": null,' \
       '                "finish_time": null,' \
       '                "start_time_json": null,' \
       '                "error_code": "",' \
       '                "error_details": "",' \
       '                "status": "exception",' \
       '                "elapsedTime": 0,' \
       '                "_isTest": true,' \
       '                "suiteVar": "",' \
       '                "SuiteName": "WA580-Open",' \
       '                "StepName": "SerialPortOpen",' \
       '                "Keyword": "SerialPortOpen",' \
       '                "ErrorCode": "3.1.0: Device.Serial.Timeout",' \
       '                "Retry": 0,' \
       '                "Timeout": 3,' \
       '                "For": "",' \
       '                "SubStr1": "",' \
       '                "SubStr2": "",' \
       '                "CmdOrParam": "COM2",' \
       '                "Param1": "",' \
       '                "ExpectStr": "9600",' \
       '                "LSL": "",' \
       '                "USL": "",' \
       '                "Unit": "",' \
       '                "_Json": "",' \
       '                "NeverUsed": null' \
       '            },' \
       '            {' \
       '                "myWind": null,' \
       '                "logger": null,' \
       '                "breakpoint": false,' \
       '                "suiteIndex": 0,' \
       '                "_index": 1,' \
       '                "testValue": null,' \
       '                "start_time": null,' \
       '                "finish_time": null,' \
       '                "start_time_json": null,' \
       '                "error_code": "",' \
       '                "error_details": "",' \
       '                "status": "exception",' \
       '                "elapsedTime": 0,' \
       '                "_isTest": true,' \
       '                "suiteVar": "",' \
       '                "SuiteName": "",' \
       '                "StepName": "ROUT Slot,Channel,On",' \
       '                "Keyword": "default",' \
       '                "ErrorCode": "3.1.0: Device.Serial.Timeout",' \
       '                "Retry": 1,' \
       '                "Timeout": 1,' \
       '                "For": "",' \
       '                "SubStr1": "",' \
       '                "SubStr2": "",' \
       '                "CmdOrParam": "ROUT 1,<CellNo>,1",' \
       '                "Param1": "",' \
       '                "ExpectStr": "OK",' \
       '                "LSL": "",' \
       '                "USL": "",' \
       '                "Unit": "",' \
       '                "_Json": "",' \
       '                "NeverUsed": null' \
       '            }' \
       '        ],' \
       '        "start_time": null,' \
       '        "finish_time": null,' \
       '        "error_code": "",' \
       '        "phase_details": "",' \
       '        "elapsedTime": null' \
       '    },' \
       '    {' \
       '        "myWind": null,' \
       '        "logger": null,' \
       '        "name": "SampleIntervalSet",' \
       '        "_index": 8,' \
       '        "isTest": true,' \
       '        "suiteResult": true,' \
       '        "isTestFinished": false,' \
       '        "totalNumber": 1,' \
       '        "suiteVar": "",' \
       '        "steps": [' \
       '            {' \
       '                "myWind": null,' \
       '                "logger": null,' \
       '                "breakpoint": false,' \
       '                "suiteIndex": 0,' \
       '                "_index": 0,' \
       '                "testValue": null,' \
       '                "start_time": null,' \
       '                "finish_time": null,' \
       '                "start_time_json": null,' \
       '                "error_code": "",' \
       '                "error_details": "",' \
       '                "status": "exception",' \
       '                "elapsedTime": 0,' \
       '                "_isTest": true,' \
       '                "suiteVar": "",' \
       '                "SuiteName": "SampleIntervalSet",' \
       '                "StepName": "Interval",' \
       '                "Keyword": "Waiting",' \
       '                "ErrorCode": "0.1.1: ThreadSleep",' \
       '                "Retry": 0,' \
       '                "Timeout": 10,' \
       '                "For": "ENDFOR",' \
       '                "SubStr1": "",' \
       '                "SubStr2": "",' \
       '                "CmdOrParam": "",' \
       '                "Param1": "",' \
       '                "ExpectStr": "",' \
       '                "LSL": "",' \
       '                "USL": "",' \
       '                "Unit": "",' \
       '                "_Json": "",' \
       '                "NeverUsed": null' \
       '            }' \
       '        ],' \
       '        "start_time": null,' \
       '        "finish_time": null,' \
       '        "error_code": "",' \
       '        "phase_details": "",' \
       '        "elapsedTime": null' \
       '    }' \
       ']'


def get_script_str(name):
    return globals()[name]


if __name__ == "__main__":
    print(get_script_str('LTT1'))
