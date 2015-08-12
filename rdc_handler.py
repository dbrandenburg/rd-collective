#!/usr/bin/env python3

import redis
import time
import subprocess
import shlex
import uuid


class CommandHandler:
    """
    Handler for pushing (master) and pulling (agent) commands to and from
    a redis queue
    """

    def __init__(self, redis_connection):
        self.r = redis_connection

    def push_command(self, nodes, command, command_expire=320):
        """
        Creates the transaction queue for receiving comman output and
        pushs command to the node's queue and returns results.
        """

        tx_id = str(uuid.uuid4())
        print("tx_id:", tx_id)
        number_of_nodes = len(nodes)
        expected_results = 0
        for nodename in nodes:
            self.r.lpush(nodename, str(tx_id + ' ' + command))
            self.r.expire(nodename, command_expire)
        expire_counter = 0
        while expected_results < number_of_nodes and expire_counter < command_expire:
            time.sleep(0.1)
            expire_counter += 0.1
            try:
                result = self.r.rpop(tx_id)
                if result:
                    expected_results += 1
                    print(result.decode("utf-8"))
            except:
                pass
        print(
            expected_results,
            'of',
            number_of_nodes,
            'nodes returned before timeout')
        return {
            'tx_id': tx_id,
            'expected': expected_results}

    def pull_commands(self, nodename, command_expire=320):
        """
        Pulls the host's command queue every second and executes command
        after extracting the UUID
        """

        while True:
            time.sleep(1)
            try:
                (tx_id, command) = str(self.r.rpop(
                    nodename).decode('ascii')).split(' ', 1)
                print('Command: ', command, 'Tx_id: ', tx_id)
                try:
                    command_output = subprocess.check_output(
                        shlex.split(command),
                        stderr=subprocess.STDOUT)
                    exit_code = 0
                except subprocess.CalledProcessError as e:
                    command_output = e.output
                    exit_code = e.returncode

                self.r.lpush(
                    tx_id, 'exit_code:' + str(exit_code) + '\n'
                    + 'node_name: ' + nodename + '\n'
                    + 'output: \n' + command_output.decode("utf-8")
                )
                self.r.expire(tx_id, command_expire)
                print(tx_id, command_output.decode("utf-8"))
            except:
                pass
