#!/usr/bin/env python3

import redis
import time
import subprocess
import shlex
import uuid
import logging
import rdc_logger


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
        
        for nodename in nodes:
            self.r.lpush(nodename, str(tx_id + ' ' + command))
            self.r.expire(nodename, command_expire)

        number_of_nodes = len(nodes)
        nodes_returnig = 0
        expire_counter = 0
        while nodes_returnig < number_of_nodes and expire_counter < command_expire:
            try:
                result = self.r.rpop(tx_id)
                if result:
                    nodes_returnig += 1
                    print(result.decode("utf-8"))
            except:
                expire_counter += 0.1
                time.sleep(0.1)

        print(
            nodes_returnig,
            'of',
            number_of_nodes,
            'nodes returned before timeout')

        return {
            'tx_id': tx_id,
            'nodes_returning': nodes_returnig,
            'number_of_nodes': number_of_nodes}

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
                logging.debug('Pulled tx_id: ' + tx_id + ' command: ' + command)
                try:
                    command_output = subprocess.check_output(
                        shlex.split(command),
                        stderr=subprocess.STDOUT)
                    exit_code = 0
                except subprocess.CalledProcessError as e:
                    command_output = e.output
                    exit_code = e.returncode
                logging.info(
                    "Executed tx_id: " + tx_id
                    + " command: " + command
                    + " exitcode: " + str(exit_code))
                self.r.lpush(
                    tx_id, 'exit_code:' + str(exit_code) + '\n'
                    + 'node_name: ' + nodename + '\n'
                    + 'output: \n' + command_output.decode("utf-8")
                )
                self.r.expire(tx_id, command_expire)
            except AttributeError:
                pass
            finally:
                self.r.delete(nodename)
