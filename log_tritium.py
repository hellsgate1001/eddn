import zlib
import zmq
import json
import sys
import time

"""
 "  Configuration
"""
__relayEDDN             = 'tcp://eddn.edcd.io:9500'
__timeoutEDDN = 600000
tritium_log = 'tritium_log.txt'



"""
 "  Start
"""
def main():
    context     = zmq.Context()
    subscriber  = context.socket(zmq.SUB)

    subscriber.setsockopt(zmq.SUBSCRIBE, b"")
    subscriber.setsockopt(zmq.RCVTIMEO, __timeoutEDDN)

    while True:
        try:
            subscriber.connect(__relayEDDN)

            while True:
                __message   = subscriber.recv()

                if __message == False:
                    subscriber.disconnect(__relayEDDN)
                    break

                __message   = zlib.decompress(__message)
                __json      = json.loads(__message)

                if __json["$schemaRef"] == "https://eddn.edcd.io/schemas/commodity/3":
                    for commodity in __json['message']['commodities']:
                        if commodity['name'].lower() == 'tritium':
                            with open(tritium_log, 'a') as f:
                                f.write(
                                    '{} \t{}\t{}\t{}\t{}\n'.format(
                                        __json['systemName'],
                                        __json['stationName'],
                                        __json['timestamp'],
                                        commodity['sellPrice'],
                                        commodity['stock']
                                    )
                                )

        except zmq.ZMQError as e:
            print ('ZMQSocketException: ' + str(e))
            sys.stdout.flush()
            subscriber.disconnect(__relayEDDN)
            time.sleep(5)



if __name__ == '__main__':
    main()
