from crelm.factory import Factory
from crelm.libcrelm import LibCrelm
from crelm.tube import Tube

from john import TestCase


class FactoryTests(TestCase):
    def test_create_libcrelm(self):
        sut = Factory(path='factory_test')

        actual = sut.create_LibCrelm()

        self.assertTrue(isinstance(actual, LibCrelm))

    def test_create_tube(self):
        sut = Factory(path='factory_test')

        actual = sut.create_Tube('test')

        self.assertTrue(isinstance(actual, Tube))
