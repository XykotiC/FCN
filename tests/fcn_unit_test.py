import unittest
import sys
sys.path.append("..")
from fcn import FCN


class FCNCheckTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_convert_hex_2byte_low(self):
        x = 0
        out = FCN.convert_to_hexbyte(x, 2)
        self.assertEqual(out, '0000')

    def test_convert_hex_4byte_low(self):
        x = 0
        out = FCN.convert_to_hexbyte(x, 4)
        self.assertEqual(out, '00000000')

    def test_convert_hex_8byte_low(self):
        x = 0
        out = FCN.convert_to_hexbyte(x, 8)
        self.assertEqual(out, '0000000000000000')

    def test_convert_hex_16byte_low(self):
        x = 0
        out = FCN.convert_to_hexbyte(x, 16)
        self.assertEqual(out, '00000000000000000000000000000000')

    def test_convert_hex_2byte_mid(self):
        x = 0
        for i in range(2*2):
            x += 16**i
        out = FCN.convert_to_hexbyte(x, 2)
        self.assertEqual(out, '1111')

    def test_convert_hex_4byte_mid(self):
        x = 0
        for i in range(4 * 2):
            x += 16 ** i
        out = FCN.convert_to_hexbyte(x, 4)
        self.assertEqual(out, '11111111')

    def test_convert_hex_8byte_mid(self):
        x = 0
        for i in range(8 * 2):
            x += 16 ** i
        out = FCN.convert_to_hexbyte(x, 8)
        self.assertEqual(out, '1111111111111111')

    def test_convert_hex_16byte_mid(self):
        x = 0
        for i in range(16 * 2):
            x += 16 ** i
        out = FCN.convert_to_hexbyte(x, 16)
        self.assertEqual(out, '11111111111111111111111111111111')

    def test_ip_valid(self):
        ip = '10.0.0.1'
        ip_checked = FCN.ip_check(address=ip)
        self.assertEqual(ip, ip_checked)

    def test_ip_check_invalid_str(self):
        ip = 'x'
        self.assertRaises(NameError, FCN.ip_check, ip)

    def test_ip_check_invalid_int(self):
        ip = 12
        self.assertRaises(NameError, FCN.ip_check, ip)

    def test_ip_check_invalid_big(self):
        ip = '256.256.256.256'
        self.assertRaises(NameError, FCN.ip_check, ip)

    def test_protocol_check_valid(self):
        for protocol in ['tcp', 'udp']:
            proto = FCN.protocol_check(protocol)
            self.assertEqual(proto, protocol)

    def test_protocol_check_invalid(self):
        for protocol in [1, 'abc']:
            self.assertRaises(NameError, FCN.protocol_check, protocol)

    def test_export_check_valid(self):
        export = 'hi'
        self.assertEqual('hi', FCN.export_name_check(export))

    def test_export_check_invalid_int(self):
        export = 1
        self.assertRaises(NameError, FCN.export_name_check, export)

    def test_export_chec_invalid_long_str(self):
        export = 'abcedefghijk'
        self.assertRaises(NameError, FCN.export_name_check, export)

    def test_msg_type_check_valid(self):
        for msg_type in [0, 1, 2]:
            self.assertEqual(msg_type, FCN.msg_type_check(msg_type))

    def test_msg_type_check_invalid_int(self):
        msg_type = 4
        self.assertRaises(NameError, FCN.msg_type_check, msg_type)

    def test_msg_type_check_invalid_str(self):
        msg_type = 'abde'
        self.assertRaises(NameError, FCN.msg_type_check, msg_type)

