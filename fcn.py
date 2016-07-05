#!/usr/local/bin/python

# Import dependencies
import socket
import sys
import time
import binascii
import argparse


class FCN:

    def __init__(self):
        # Get command line inputs
        inputs = self.parser()

        # Serialise data
        c_msg = self.create_msg_payload(inputs=inputs)
        c_temp = self.create_template(payload_len=len(c_msg))
        c_header = self.create_header(inputs=inputs,
                                      payload_len=len(c_msg),
                                      template_len=len(c_temp))

        rap = binascii.a2b_hex(c_msg + c_temp + c_header)

        # Send RAP message
        self.sock_open(rap, inputs)

    def create_msg_payload(self, inputs):
        packet_count = 0
        kbyte_count = 0

        # Var
        msg_type = self.msg_type_check(inputs.msgtype)
        prototype = self.prototype_check(inputs.prototype)
        export_name = self.export_name_check(inputs.export)
        table_priority = self.priority_check(inputs.prio)
        source_port = self.port_check(inputs.srcport)
        destination_port = self.port_check(inputs.destport)
        class_name = inputs.mclass

        # Create & Check Src IP
        try:
            source_ip = self.ip_check(inputs.srcip)
            source_ip = source_ip.split('.')
            for i, j in enumerate(source_ip):
                source_ip[i] = int(j)
        except IndexError:
            sys.exit('Error: Invalid Source IP address detected')

        # Create & Check Dst IP
        try:
            destination_ip = self.ip_check(inputs.destip)
            destination_ip = destination_ip.split('.')
            for i, j in enumerate(destination_ip):
                destination_ip[i] = int(j)
        except IndexError:
            sys.exit('Error: Invalid Source IP address detected')

        # Assign data variables from CLI
        o_expname = export_name.encode('hex').ljust(16, '0')
        o_msgtype = self.convert_to_hex(msg_type, 1)
        o_srcip = (self.convert_to_hex(source_ip[0], 1)
                   + self.convert_to_hex(source_ip[1], 1)
                   + self.convert_to_hex(source_ip[2], 1)
                   + self.convert_to_hex(source_ip[3], 1))
        o_destip = (self.convert_to_hex(destination_ip[0], 1)
                    + self.convert_to_hex(destination_ip[1], 1)
                    + self.convert_to_hex(destination_ip[2], 1)
                    + self.convert_to_hex(destination_ip[3], 1))
        o_srcport = self.convert_to_hex(source_port, 2)
        o_destport = self.convert_to_hex(destination_port, 2)
        o_proto = self.convert_to_hex(prototype, 1)
        o_packetcount = self.convert_to_hex(packet_count, 4)
        o_kbyte_count = self.convert_to_hex(kbyte_count, 4)
        o_class_len = self.convert_to_hex(len(class_name) + 4, 1)
        o_classname = class_name.encode('hex').ljust(
            len(inputs.mclass) * 2 + 4, '0')
        o_classprio = self.convert_to_hex(table_priority, 1)
        o_t_type = self.convert_to_hex(0, 1)
        o_t_val = self.convert_to_hex(inputs.timeoutval, 2)
        o_act = self.convert_to_hex(0, 8)
        o_act_flg = self.convert_to_hex(inputs.a_flg, 2)
        o_act_par = self.convert_to_hex(0, 16)

        # Create data section
        msg = (o_expname
               + o_msgtype
               + o_srcip
               + o_destip
               + o_srcport
               + o_destport
               + o_proto
               + o_packetcount
               + o_kbyte_count
               + o_class_len
               + o_classname
               + o_classprio
               + o_t_type
               + o_t_val
               + o_act
               + o_act_flg
               + o_act_par)

        return msg

    def create_template(self, payload_len):

        class TemplateClass:
            t_id = self.convert_to_hex(256, 2)
            t_flag = self.convert_to_hex(0, 2)
            NOP = self.convert_to_hex(0, 2)  # 0
            SRC_IPV4 = self.convert_to_hex(1, 2)  # 1
            DST_IPV4 = self.convert_to_hex(2, 2)  # 2
            SRC_PORT = self.convert_to_hex(3, 2)  # 3
            DST_PORT = self.convert_to_hex(4, 2)  # 4
            PROTO = self.convert_to_hex(5, 2)  # 5
            # SRC_IPV6=         self.byte_conv(6,2) #6
            # DST_IPV6=         self.byte_conv(7,2) #7
            IPV4_TOS = self.convert_to_hex(8, 2)  # 8
            IPV6_LABEL = self.convert_to_hex(9, 2)  # 9
            CLASS_LABEL = self.convert_to_hex(10, 2)  # a
            MATCH_DIR = self.convert_to_hex(11, 2)  # b
            MSG_TYPE = self.convert_to_hex(12, 2)  # c
            TIMEOUT_TYPE = self.convert_to_hex(13, 2)  # d
            TIMEOUT = self.convert_to_hex(14, 2)  # e
            ACTION_FLAGS = self.convert_to_hex(15, 2)  # f
            PCKT_CNT = self.convert_to_hex(16, 2)  # 10
            KBYTE_CNT = self.convert_to_hex(17, 2)  # 11
            ACTION = self.convert_to_hex(32768, 2)  # 8000	#
            ACTION_PARAMS = self.convert_to_hex(32769, 2)  # 8001   #
            EXPORT_NAME = self.convert_to_hex(32770, 2)  # 8002	#
            CLASSIFIER_NAME = self.convert_to_hex(32771, 2)  # 8003	#
            CLASSES = self.convert_to_hex(49152, 2)  # C000	#
            set_id = 0
            set_len = 0

        ts = TemplateClass

        # Optionals
        len_exp = self.convert_to_hex(8, 2)  # Length of export name
        len_act = self.convert_to_hex(8, 2)  # Length of action
        len_actp = self.convert_to_hex(16, 2)  # Length of action parameter

        ts.set_id = self.convert_to_hex(256, 2)  # Set ID = 256 for msg
        ts.set_len = self.convert_to_hex(
            payload_len / 2 + 4, 2)  # Set length of msg

        # Create template section
        temp = (ts.t_id +
                ts.t_flag
                + ts.EXPORT_NAME
                + len_exp
                + ts.MSG_TYPE
                + ts.SRC_IPV4
                + ts.DST_IPV4
                + ts.SRC_PORT
                + ts.DST_PORT
                + ts.PROTO
                + ts.PCKT_CNT
                + ts.KBYTE_CNT
                + ts.CLASSES
                + ts.TIMEOUT_TYPE
                + ts.TIMEOUT
                + ts.ACTION
                + len_act
                + ts.ACTION_FLAGS
                + ts.ACTION_PARAMS
                + len_actp
                + ts.set_id
                + ts.set_len)

        return temp

    def sock_open(self, buff, inputs):
        # Host socket assign
        port = self.port_check(inputs.PORT)
        proto = self.protocol_check(inputs.PROTO)  # Proto check

        try:
            if proto.lower() in ["udp"]:
                print
                "Opening UDP socket on port", port
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            else:
                print
                "Opening TCP socket on port", port
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if proto.lower() in ["udp"]:
                sock.sendto(buff, (inputs.HOST, port))
            else:
                BUFFER = 1024
                sock.settimeout(10)
                sock.connect((inputs.HOST, port))
                sock.send(buff)
                sock.close()

        except(socket.timeout):
            sys.exit('Error: Couldn\'t connect to socket')

    def create_header(self, cli_inputs, payload_len, template_len):
        """Creates the packet header

        Parameters
        ----------
        cli_inputs:
            The imported command line interface inputs
        payload_len:
            The length of the payload packet
        template_len:
            The length of the template

        Returns
        -------
        header: Tuple
            The header information

        """
        # Get current time
        current_time = int(time.time())

        # Create initial header variables
        ver = self.convert_to_hex(_input=1, _len=2)
        seq_no = cli_inputs.seq_no
        time_hexed = self.convert_to_hex(_input=current_time, _len=4)
        set_id = self.convert_to_hex(1, 2)  # Set ID = 1 for template
        set_len = self.convert_to_hex(
            template_len / 2, 2)  # Set length of template
        m_len = self.convert_to_hex((payload_len + template_len) / 2 + 16,
                                    2)  # Size of payload
        # Create header
        header = (str(ver)
                  + str(seq_no)
                  + str(time_hexed)
                  + str(set_id)
                  + str(set_len)
                  + str(m_len))

        return header

    @staticmethod
    def parser():
        """Command Line Interface for the FCN

        Returns
        -------
        args:
            The command line interface inputs

        """
        parser = argparse.ArgumentParser(
            description='CLI Scanning Utility\n',
            formatter_class=argparse.RawTextHelpFormatter)

        parser.add_argument('-i', '--srcip',
                            action="store",
                            dest="srcip",
                            default='0.0.0.0',
                            metavar='Source IP',
                            help="\t\t\tSource IP address in x.x.x.x format")
        parser.add_argument("-j", "--destip",
                            action="store",
                            dest="destip",
                            default='0.0.0.0',
                            # required = True,
                            metavar='Destination IP',
                            help='\t\t\tDestination IP address in x.x.x.x format')
        parser.add_argument("-s", "--seqno",
                            action="store",
                            dest="seq_no",
                            type=int,
                            # required = True,
                            default=20,
                            metavar='Sequence Number',
                            help='\t\t\tSequence Number')
        parser.add_argument("-k", "--srcport",
                            action="store",
                            dest="srcport",
                            type=int,
                            default=0,
                            metavar='Source port',
                            help='\t\t\tSource port 1-65535')
        parser.add_argument("-l", "--destport",
                            action="store",
                            dest="destport",
                            type=int,
                            default=0,
                            metavar='Destination port',
                            help='\t\t\tDestination port 1-65535')
        parser.add_argument("-u", "--prototype",
                            action="store",
                            dest="prototype",
                            type=int,
                            default=0,  # nothin
                            metavar='Protocol Type',
                            help='\t\t\t'
                                 'Protocol Type (Default: TCP)\n\t\t\t'
                                 '1: ICMP\n\t\t\t'
                                 '2: IGMP\n\t\t\t'
                                 '3: GGP\n\t\t\t'
                                 '4: IPENCAP\n\t\t\t'
                                 '5: ST2\n\t\t\t'
                                 '6: TCP\n\t\t\t'
                                 '17: UDP\n')
        # 7cbt#8egp#9ip
        parser.add_argument("-a", '--mtype',
                            action="store",
                            dest="msgtype",
                            type=int,
                            default=0,
                            metavar='Msg Type',
                            help='\t\t\t'
                                 '0: Add (Default)\n\t\t\t'
                                 '1: Remove\n\t\t\t'
                                 '2: Remove All\n')
        parser.add_argument(
            "-t",
            "--timeoutval",
            action="store",
            dest="timeoutval",
            type=int,
            default=60,
            metavar='Timeout Value',
            help='\t\t\tTimeout value in seconds (Default: 60)')
        parser.add_argument("-e", "--export",
                            action="store",
                            dest="export",
                            default='myexp',
                            metavar='Export',
                            help='\t\t\tName of export (Default: myexp)')
        parser.add_argument("-c", "--class",
                            action="store",
                            dest="mclass",
                            default='myclass',
                            metavar='Class',
                            help='\t\t\t'
                                 'Name of class (Default: myclass)')
        parser.add_argument("-n", "--prio",
                            action="store",
                            dest="prio",
                            type=int,
                            default=1,
                            metavar='Priority',
                            help='\t\t\t'
                                 'Class Priority (Default: 1)')
        # Global
        parser.add_argument("-x", "--host",
                            action="store",
                            dest="HOST",
                            default='127.0.0.1',
                            metavar='Host',
                            help='\n\t\t\t'
                                 'Action Node IP (Default: 127.0.0.1)')
        parser.add_argument("-y", "--port",
                            action="store",
                            dest="PORT",
                            type=int,
                            default=5000,
                            metavar='Port',
                            help='\n\t\t\t'
                                 'Output Port to Action Node (Default: 5000)')
        parser.add_argument("-z", "--proto",
                            action="store",
                            dest="PROTO",
                            default='UDP',
                            metavar='Proto',
                            help='\t\t\t'
                                 'Protocol to Action Node (Default: UDP)')
        parser.add_argument("-o",  # uni/bidirectional to be added
                            action="store",
                            dest="a_flg",
                            type=int,
                            default=1,
                            metavar='Action Flag',
                            help='(Experimental)\n\t\t\t'
                                 '0: Unidirectional\n\t\t\t'
                                 '1: Bidirectional\n')
        cli_inputs = parser.parse_args()

        return cli_inputs

    @staticmethod
    def port_check(port):
        if 0 <= port <= 65535:
            return port
        else:
            sys.exit(
                'Error: '
                'Flow Source/Destination port must be between 0 and 65535')

    @staticmethod
    def priority_check(priority):
        if 0 <= priority < 256:
            return priority
        else:
            sys.exit('Error: Priority must be between 0 and 255')

    @staticmethod
    def prototype_check(prototype):
        if 0 <= prototype < 256:
            return prototype
        else:
            sys.exit('Error: Invalid protocol type')

    @staticmethod
    def msg_type_check(msg_type):
        if 0 <= msg_type < 5:
            return msg_type
        else:
            sys.exit('Error: Msg type must be between 0-2')

    @staticmethod
    def export_name_check(export_name):
        if len(export_name) <= 8:
            return export_name
        else:
            sys.exit('Error: Class Name is too long')

    @staticmethod
    def protocol_check(protocol):
        if protocol.lower() in ["tcp", "udp"]:
            return protocol
        else:
            sys.exit("Error: only UDP or TCP supported")

    @staticmethod
    def ip_check(addr):
        socket.inet_pton(socket.AF_INET, addr)
        return addr

    @staticmethod
    def convert_to_hex(_input, _len):
        if _len == 1:
            _input = '{:0>2x}'.format(_input)
            _input = '{:.2}'.format(_input)
        elif _len == 2:
            _input = '{:0>4x}'.format(_input)
            _input = '{:.4}'.format(_input)
        elif _len == 4:
            _input = '{:0>8x}'.format(_input)
            _input = '{:.8}'.format(_input)
        elif _len == 8:
            _input = '{:0>16x}'.format(_input)
            _input = '{:.16}'.format(_input)
        elif _len == 16:
            _input = '{:0>32x}'.format(_input)
            _input = '{:.32}'.format(_input)
        else:
            print('Error: Variable couldn\'t be converted')
        return _input

if __name__ == '__main__':
    FCN()