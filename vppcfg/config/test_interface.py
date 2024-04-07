#
# Copyright (c) 2022 Pim van Pelt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-
""" Unit tests for interfaces """
import unittest
import yaml
from . import interface
from .unittestyaml import UnitTestYaml


class TestInterfaceMethods(unittest.TestCase):
    def setUp(self):
        with UnitTestYaml("test_interface.yaml") as f:
            self.cfg = yaml.load(f, Loader=yaml.FullLoader)

    def test_enumerators(self):
        ifs = interface.get_interfaces(self.cfg)
        self.assertEqual(len(ifs), 27)
        self.assertIn("GigabitEthernet1/0/1", ifs)
        self.assertIn("GigabitEthernet1/0/1.200", ifs)

        ifs = interface.get_sub_interfaces(self.cfg)
        self.assertEqual(len(ifs), 17)
        self.assertNotIn("GigabitEthernet1/0/1", ifs)
        self.assertIn("GigabitEthernet1/0/1.200", ifs)
        self.assertIn("GigabitEthernet1/0/1.201", ifs)
        self.assertIn("GigabitEthernet1/0/1.202", ifs)
        self.assertIn("GigabitEthernet1/0/1.203", ifs)

        ifs = interface.get_qinx_interfaces(self.cfg)
        self.assertEqual(len(ifs), 3)
        self.assertNotIn("GigabitEthernet1/0/1.200", ifs)
        self.assertNotIn("GigabitEthernet1/0/1.202", ifs)
        self.assertIn("GigabitEthernet1/0/1.201", ifs)
        self.assertIn("GigabitEthernet1/0/1.203", ifs)

        ifs = interface.get_l2xc_interfaces(self.cfg)
        self.assertEqual(len(ifs), 3)
        self.assertIn("GigabitEthernet3/0/0", ifs)
        self.assertIn("GigabitEthernet3/0/1", ifs)
        self.assertIn("GigabitEthernet3/0/2.100", ifs)
        self.assertNotIn("GigabitEthernet3/0/2.200", ifs)

        target_ifs = interface.get_l2xc_target_interfaces(self.cfg)
        self.assertEqual(len(target_ifs), 3)
        self.assertIn("GigabitEthernet3/0/0", target_ifs)
        self.assertIn("GigabitEthernet3/0/1", target_ifs)
        self.assertNotIn("GigabitEthernet3/0/2.100", target_ifs)
        self.assertIn("GigabitEthernet3/0/2.200", target_ifs)

        ## Since l2xc cannot connect to itself, and the target must exist,
        ## it follows that the same number of l2xc target interfaces must exist.
        self.assertEqual(len(target_ifs), len(ifs))

    def test_mtu(self):
        self.assertEqual(interface.get_mtu(self.cfg, "GigabitEthernet1/0/1"), 9216)
        self.assertEqual(interface.get_mtu(self.cfg, "GigabitEthernet1/0/1.200"), 9000)
        self.assertEqual(interface.get_mtu(self.cfg, "GigabitEthernet1/0/1.201"), 9216)

    def test_encapsulation(self):
        self.assertTrue(
            interface.valid_encapsulation(self.cfg, "GigabitEthernet1/0/1.200")
        )
        self.assertTrue(
            interface.unique_encapsulation(self.cfg, "GigabitEthernet1/0/1.200")
        )
        self.assertEqual(
            interface.get_encapsulation(self.cfg, "GigabitEthernet1/0/1.200"),
            {"dot1q": 1000, "dot1ad": 0, "inner-dot1q": 0, "exact-match": False},
        )
        self.assertEqual(
            interface.get_encapsulation(self.cfg, "GigabitEthernet1/0/1.201"),
            {"dot1q": 1000, "dot1ad": 0, "inner-dot1q": 1234, "exact-match": False},
        )
        self.assertEqual(
            interface.get_encapsulation(self.cfg, "GigabitEthernet1/0/1.202"),
            {"dot1q": 0, "dot1ad": 1000, "inner-dot1q": 0, "exact-match": False},
        )
        self.assertEqual(
            interface.get_encapsulation(self.cfg, "GigabitEthernet1/0/1.203"),
            {"dot1q": 0, "dot1ad": 1000, "inner-dot1q": 1000, "exact-match": True},
        )

        self.assertFalse(
            interface.valid_encapsulation(self.cfg, "GigabitEthernet1/0/0.100")
        )
        self.assertFalse(
            interface.valid_encapsulation(self.cfg, "GigabitEthernet1/0/0.101")
        )

        self.assertFalse(
            interface.unique_encapsulation(self.cfg, "GigabitEthernet1/0/0.102")
        )
        self.assertFalse(
            interface.unique_encapsulation(self.cfg, "GigabitEthernet1/0/0.103")
        )

    def test_has_sub(self):
        self.assertTrue(interface.has_sub(self.cfg, "GigabitEthernet1/0/1"))
        self.assertFalse(interface.has_sub(self.cfg, "GigabitEthernet1/0/1.200"))
        self.assertFalse(interface.has_sub(self.cfg, "GigabitEthernet2/0/0"))
        self.assertFalse(interface.has_sub(self.cfg, "GigabitEthernet3/0/0"))

    def test_is_sub(self):
        self.assertFalse(interface.is_sub(self.cfg, "GigabitEthernet1/0/1"))
        self.assertTrue(interface.is_sub(self.cfg, "GigabitEthernet1/0/1.200"))

    def test_is_qinx(self):
        self.assertFalse(interface.is_qinx(self.cfg, "GigabitEthernet1/0/1"))
        self.assertFalse(interface.is_qinx(self.cfg, "GigabitEthernet1/0/1.200"))
        self.assertFalse(interface.is_qinx(self.cfg, "GigabitEthernet1/0/1.202"))

        self.assertTrue(interface.is_qinx(self.cfg, "GigabitEthernet1/0/1.201"))
        self.assertTrue(interface.is_qinx(self.cfg, "GigabitEthernet1/0/1.203"))

    def test_has_lcp(self):
        self.assertTrue(interface.has_lcp(self.cfg, "GigabitEthernet1/0/1"))
        self.assertFalse(interface.has_lcp(self.cfg, "GigabitEthernet1/0/0"))

    def test_get_lcp(self):
        self.assertIsNone(interface.get_lcp(self.cfg, "GigabitEthernet1/0/0"))
        self.assertIsNone(interface.get_lcp(self.cfg, "GigabitEthernet1/0/0.100"))

        self.assertEqual(interface.get_lcp(self.cfg, "GigabitEthernet1/0/1"), "e1")
        self.assertEqual(interface.get_lcp(self.cfg, "GigabitEthernet1/0/1.100"), "foo")
        self.assertEqual(
            interface.get_lcp(self.cfg, "GigabitEthernet1/0/1.101"), "e1.100"
        )
        self.assertEqual(
            interface.get_lcp(self.cfg, "GigabitEthernet1/0/1.102"), "e1.100.100"
        )

        self.assertIsNone(interface.get_lcp(self.cfg, "GigabitEthernet1/0/1.200"))
        self.assertIsNone(interface.get_lcp(self.cfg, "GigabitEthernet1/0/1.201"))
        self.assertIsNone(interface.get_lcp(self.cfg, "GigabitEthernet1/0/1.202"))
        self.assertIsNone(interface.get_lcp(self.cfg, "GigabitEthernet1/0/1.203"))

    def test_address(self):
        self.assertFalse(interface.has_address(self.cfg, "GigabitEthernet1/0/0"))
        self.assertFalse(interface.has_address(self.cfg, "GigabitEthernet1/0/0.100"))

        self.assertTrue(interface.has_address(self.cfg, "GigabitEthernet1/0/1"))
        self.assertTrue(interface.has_address(self.cfg, "GigabitEthernet1/0/1.100"))

    def test_lx2c(self):
        l2xc_ifs = interface.get_l2xc_interfaces(self.cfg)
        l2xc_target_ifs = interface.get_l2xc_target_interfaces(self.cfg)

        self.assertIn("GigabitEthernet3/0/0", l2xc_ifs)
        self.assertIn("GigabitEthernet3/0/0", l2xc_target_ifs)
        self.assertTrue(interface.is_l2xc_interface(self.cfg, "GigabitEthernet3/0/0"))
        self.assertTrue(
            interface.is_l2xc_target_interface(self.cfg, "GigabitEthernet3/0/0")
        )

        self.assertNotIn("GigabitEthernet2/0/0", l2xc_ifs)
        self.assertNotIn("GigabitEthernet2/0/0", l2xc_target_ifs)
        self.assertFalse(interface.is_l2xc_interface(self.cfg, "GigabitEthernet2/0/0"))
        self.assertFalse(
            interface.is_l2xc_target_interface(self.cfg, "GigabitEthernet2/0/0")
        )

    def test_l2(self):
        self.assertTrue(interface.is_l2(self.cfg, "GigabitEthernet3/0/0"))
        self.assertFalse(interface.is_l2(self.cfg, "GigabitEthernet1/0/0"))
        self.assertTrue(interface.is_l2(self.cfg, "GigabitEthernet3/0/2.100"))
        self.assertTrue(interface.is_l2(self.cfg, "GigabitEthernet3/0/2.200"))

    def test_l3(self):
        self.assertTrue(interface.is_l3(self.cfg, "GigabitEthernet1/0/0"))
        self.assertFalse(interface.is_l3(self.cfg, "GigabitEthernet3/0/0"))

    def test_get_by_lcp_name(self):
        ifname, iface = interface.get_by_lcp_name(self.cfg, "notexist")
        self.assertIsNone(ifname)
        self.assertIsNone(iface)

        ifname, iface = interface.get_by_lcp_name(self.cfg, "e1.100.100")
        self.assertEqual(ifname, "GigabitEthernet1/0/1.102")
        ifname, iface = interface.get_by_lcp_name(self.cfg, "e2")
        self.assertEqual(ifname, "GigabitEthernet2/0/0")

    def test_get_by_name(self):
        ifname, iface = interface.get_by_name(self.cfg, "GigabitEthernet1/0/1.201")
        self.assertEqual(ifname, "GigabitEthernet1/0/1.201")
        self.assertIsNotNone(iface)
        encap = interface.get_encapsulation(self.cfg, ifname)
        self.assertEqual(
            encap,
            {"dot1q": 1000, "dot1ad": 0, "inner-dot1q": 1234, "exact-match": False},
        )

        ifname, iface = interface.get_by_name(self.cfg, "GigabitEthernet1/0/1.1")
        self.assertIsNone(ifname)
        self.assertIsNone(iface)

    def test_get_parent_by_name(self):
        ifname, iface = interface.get_parent_by_name(
            self.cfg, "GigabitEthernet1/0/1.201"
        )
        self.assertEqual(ifname, "GigabitEthernet1/0/1")
        self.assertIsNotNone(iface)
        self.assertNotIn("encapsulation", iface)

        ifname, iface = interface.get_parent_by_name(
            self.cfg, "GigabitEthernet1/0/1.200"
        )
        self.assertEqual(ifname, "GigabitEthernet1/0/1")
        self.assertIsNotNone(iface)
        self.assertNotIn("encapsulation", iface)

        ifname, iface = interface.get_parent_by_name(self.cfg, "GigabitEthernet1/0/1")
        self.assertIsNone(ifname)
        self.assertIsNone(iface)

        ifname, iface = interface.get_parent_by_name(self.cfg, None)
        self.assertIsNone(ifname)
        self.assertIsNone(iface)

    def test_get_qinx_parent_by_name(self):
        self.assertIsNotNone(
            interface.get_qinx_parent_by_name(self.cfg, "GigabitEthernet1/0/1.202")
        )
        self.assertIsNotNone(
            interface.get_qinx_parent_by_name(self.cfg, "GigabitEthernet1/0/1.203")
        )

        ifname, iface = interface.get_qinx_parent_by_name(
            self.cfg, "GigabitEthernet1/0/1"
        )
        self.assertIsNone(iface)
        self.assertIsNone(ifname)

        ifname, iface = interface.get_qinx_parent_by_name(
            self.cfg, "GigabitEthernet1/0/1.100"
        )
        self.assertIsNone(iface)
        self.assertIsNone(ifname)

        ifname, iface = interface.get_qinx_parent_by_name(
            self.cfg, "GigabitEthernet1/0/1.200"
        )
        self.assertIsNone(iface)
        self.assertIsNone(ifname)

        ifname, iface = interface.get_qinx_parent_by_name(
            self.cfg, "GigabitEthernet1/0/1.201"
        )
        self.assertEqual(ifname, "GigabitEthernet1/0/1.200")

    def test_get_phys(self):
        phys = interface.get_phys(self.cfg)
        self.assertEqual(len(phys), 10)
        self.assertIn("GigabitEthernet1/0/0", phys)
        self.assertNotIn("GigabitEthernet1/0/0.100", phys)

    def test_is_phy(self):
        self.assertTrue(interface.is_phy(self.cfg, "GigabitEthernet1/0/0"))
        self.assertFalse(interface.is_phy(self.cfg, "GigabitEthernet1/0/0.100"))

    def test_get_admin_state(self):
        self.assertFalse(interface.get_admin_state(self.cfg, "notexist"))
        self.assertFalse(interface.get_admin_state(self.cfg, "GigabitEthernet2/0/0"))
        self.assertTrue(interface.get_admin_state(self.cfg, "GigabitEthernet1/0/0"))
        self.assertTrue(interface.get_admin_state(self.cfg, "GigabitEthernet1/0/0.101"))
        self.assertFalse(
            interface.get_admin_state(self.cfg, "GigabitEthernet1/0/0.102")
        )

    def test_is_mpls(self):
        self.assertTrue(interface.is_mpls(self.cfg, "GigabitEthernet1/0/1"))
        self.assertTrue(interface.is_mpls(self.cfg, "GigabitEthernet1/0/1.101"))
        self.assertFalse(interface.is_mpls(self.cfg, "GigabitEthernet1/0/0"))
        self.assertFalse(interface.is_mpls(self.cfg, "GigabitEthernet1/0/0.100"))
        self.assertFalse(interface.is_mpls(self.cfg, "notexist"))

    def test_get_unnumbered_interfaces(self):
        unnumbered_ifaces = interface.get_unnumbered_interfaces(self.cfg)
        self.assertEqual(len(unnumbered_ifaces), 5)
        self.assertNotIn("GigabitEthernet4/0/0", unnumbered_ifaces)
        self.assertIn("GigabitEthernet4/0/1", unnumbered_ifaces)
        self.assertNotIn("GigabitEthernet4/0/3.100", unnumbered_ifaces)
        self.assertIn("GigabitEthernet4/0/3.101", unnumbered_ifaces)

    def test_is_unnumbered(self):
        self.assertFalse(interface.is_unnumbered(self.cfg, "GigabitEthernet4/0/0"))
        self.assertTrue(interface.is_unnumbered(self.cfg, "GigabitEthernet4/0/1"))
        self.assertTrue(interface.is_unnumbered(self.cfg, "GigabitEthernet4/0/2"))
        self.assertFalse(interface.is_unnumbered(self.cfg, "GigabitEthernet4/0/3.100"))
        self.assertTrue(interface.is_unnumbered(self.cfg, "GigabitEthernet4/0/3.101"))
        self.assertTrue(interface.is_unnumbered(self.cfg, "GigabitEthernet4/0/3.102"))
        self.assertTrue(interface.is_unnumbered(self.cfg, "GigabitEthernet4/0/3.103"))
