import cStringIO

_s0 = {
	0xA1 : u'\x01\x41', 0xA2 : u'\xD8',	0xA3 : u'\x01\x10',
	0xA4 : u'\xDE',	    0xA5 : u'\xC6',	0xA6 : u'\x01\x52',
	0xA7 : u'\x02\xB9', 0xA8 : u'\xB7',	0xA9 : u'\x26\x6D',
	0xAA : u'\xAE',	    0xAB : u'\xB1',	0xAC : u'\x01\xA0',
	0xAD : u'\x01\xAF', 0xAE : u'\x02\xBC',	0xB0 : u'\x02\xBB',
	0xB1 : u'\x01\x42', 0xB2 : u'\xF8',	0xB3 : u'\x01\x11',
	0xB4 : u'\xFE',	    0xB5 : u'\xE6',	0xB6 : u'\x01\x53',
	0xB7 : u'\x02\xBA', 0xB8 : u'\x01\x31',	0xB9 : u'\xA3',
	0xBA : u'\xF0',	    0xBC : u'\x01\xA1',	0xBD : u'\x01\xB0',
	0xC0 : u'\xB0',	    0xC1 : u'\x21\x13',	0xC2 : u'\x21\x17',
	0xC3 : u'\xA9',	    0xC4 : u'\x26\x6F',	0xC5 : u'\xBF',
	0xC6 : u'\xA1',	    0xCF : u'\xDF',	0xE1 : u'\x03\x00',
	0xE2 : u'\x03\x01', 0xE3 : u'\x03\x02',	0xE4 : u'\x03\x03',
	0xE5 : u'\x03\x04', 0xE6 : u'\x03\x06',	0xE7 : u'\x03\x07',
	0xE8 : u'\x03\x08', 0xE9 : u'\x03\x0C',	0xEA : u'\x03\x0A',
	0xEB : u'\xFE\x20', 0xEC : u'\xFE\x21',	0xED : u'\x03\x15',
	0xEE : u'\x03\x0B', 0xEF : u'\x03\x10',	0xF0 : u'\x03\x27',
	0xF1 : u'\x03\x28', 0xF2 : u'\x03\x23',	0xF3 : u'\x03\x24',
	0xF4 : u'\x03\x25', 0xF5 : u'\x03\x33',	0xF6 : u'\x03\x32',
	0xF7 : u'\x03\x26', 0xF8 : u'\x03\x21',	0xF9 : u'\x03\x2E',
	0xFA : u'\xFE\x22', 0xFB : u'\xFE\x23',	0xE0 : u'\x03\x09',
}

_e0 = {
	0x41 : u'\x1E\xA2', 0x45 : u'\x1E\xBA', 0x49 : u'\x1E\xC8',
	0x4F : u'\x1E\xCE', 0x55 : u'\x1E\xE6',	0x59 : u'\x1E\xF6',
	0x61 : u'\x1E\xA3', 0x65 : u'\x1E\xBB', 0x69 : u'\x1E\xC9',
	0x6F : u'\x1E\xCF', 0x75 : u'\x1E\xE7', 0x79 : u'\x1E\xF7',
}

_e0e3 = {
	0x41 : u'\x1E\xA8', 0x45 : u'\x1E\xC2',	0x4F : u'\x1E\xD4',
	0x61 : u'\x1E\xA9', 0x65 : u'\x1E\xC3',	0x6F : u'\x1E\xD5',
}

_e0e6 = {
	0x41 : u'\x1E\xB2', 0x61 : u'\x1E\xB3',
}

_e1 = {
	0x41 : u'\xC0',     0x45 : u'\xC8',	0x49 : u'\xCC',
	0x4F : u'\xD2',     0x55 : u'\xD9',	0x57 : u'\x1E\x80',
	0x59 : u'\x1E\xF2', 0x61 : u'\xE0',	0x65 : u'\xE8',
	0x69 : u'\xEC',     0x6F : u'\xF2',	0x75 : u'\xF9',
	0x77 : u'\x1E\x81', 0x79 : u'\x1E\xF3',
}

_e1e3 = { 
	0x41 : u'\x1E\xA6', 0x45 : u'\x1E\xC0',	0x4F : u'\x1E\xD2',
	0x61 : u'\x1E\xA7', 0x65 : u'\x1E\xC1',	0x6F : u'\x1E\xD3',
}

_e1e5 = {
	0x45 : u'\x1E\x14', 0x4F : u'\x1E\x50',	0x65 : u'\x1E\x15',
	0x6F : u'\x1E\x51',
}

_e1e6 = {
	0x41 : u'\x1E\xB0', 0x61 : u'\x1E\xB1',
}

_e1e8 = {
	0x55 : u'\x01\xDB', 0x75 : u'\x01\xDC',
}

_e2 = {
	0x41 : u'\xC1',     0x43 : u'\x01\x06',	0x45 : u'\xC9',
	0x47 : u'\x01\xF4', 0x49 : u'\xCD',	0x4B : u'\x1E\x30',
	0x4C : u'\x01\x39', 0x4D : u'\x1E\x3E',	0x4E : u'\x01\x43',
	0x4F : u'\xD3',     0x50 : u'\x1E\x54',	0x52 : u'\x01\x54',
	0x53 : u'\x01\x5A', 0x55 : u'\xDA',	0x57 : u'\x1E\x82',
	0x59 : u'\xDD',     0x5A : u'\x01\x79',	0x61 : u'\xE1',
	0x63 : u'\x01\x07', 0x65 : u'\xE9',	0x67 : u'\x01\xF5',
	0x69 : u'\xED',     0x6B : u'\x1E\x31',	0x6C : u'\x01\x3A',
	0x6D : u'\x1E\x3F', 0x6E : u'\x01\x44',	0x6F : u'\xF3',
	0x70 : u'\x1E\x55', 0x72 : u'\x01\x55',	0x73 : u'\x01\x5B',
	0x75 : u'\xFA',     0x77 : u'\x1E\x83',	0x79 : u'\xFD',
	0x7A : u'\x01\x7A', 0xA5 : u'\x01\xFC',	0xB5 : u'\x01\xFD',
}

_e2e3 = {
	0x41 : u'\x1E\xA4', 0x45 : u'\x1E\xBE',	0x4F : u'\x1E\xD0',
	0x61 : u'\x1E\xA5', 0x65 : u'\x1E\xBF',	0x6F : u'\x1E\xD1',
}

_e2e4 = {
	0x4F : u'\x1E\x4C', 0x55 : u'\x1E\x78',	0x6F : u'\x1E\x4D',
	0x75 : u'\x1E\x79',
}

_e2e5 = {
	0x45 : u'\x1E\x16', 0x4F : u'\x1E\x52',	0x65 : u'\x1E\x17',
	0x6F : u'\x1E\x53',
}

_e2e6 = {
	0x41 : u'\x1E\xAE', 0x61 : u'\x1E\xAF',
}

_e2e7 = {
	0x53 : u'\x1E\x64', 0x73 : u'\x1E\x65',
}

_e2e8 = {
	0x49 : u'\x1E\x2E', 0x55 : u'\x01\xD7',	0x69 : u'\x1E\x2F',
	0x75 : u'\x01\xD8',
}

_e2ea = {
	0x41 : u'\x01\xFA', 0x61 : u'\x01\xFB',
}

_e2f0 = {
	0x43 : u'\x1E\x08', 0x63 : u'\x1E\x09',
}

_e3 = {
	0x41 : u'\xC2',     0x43 : u'\x01\x08',	0x45 : u'\xCA',
	0x47 : u'\x01\x1C', 0x48 : u'\x01\x24',	0x49 : u'\xCE',
	0x4A : u'\x01\x34', 0x4F : u'\xD4',	0x53 : u'\x01\x5C',
	0x55 : u'\xDB',     0x57 : u'\x01\x74',	0x59 : u'\x01\x76',
	0x5A : u'\x1E\x90', 0x61 : u'\xE2',	0x63 : u'\x01\x09',
	0x65 : u'\xEA',     0x67 : u'\x01\x1D',	0x68 : u'\x01\x25',
	0x69 : u'\xEE',     0x6A : u'\x01\x35',	0x6F : u'\xF4',
	0x73 : u'\x01\x5D', 0x75 : u'\xFB',	0x77 : u'\x01\x75',
	0x79 : u'\x01\x77', 0x7A : u'\x1E\x91',
}

_e3e0 = {
	0x41 : u'\x1E\xA8', 0x45 : u'\x1E\xC2',	0x4F : u'\x1E\xD4',
	0x61 : u'\x1E\xA9', 0x65 : u'\x1E\xC3',	0x6F : u'\x1E\xD5',
}
_e3e1 = {
	0x41 : u'\x1E\xA6', 0x45 : u'\x1E\xC0', 0x4F : u'\x1E\xD2',
	0x61 : u'\x1E\xA7', 0x65 : u'\x1E\xC1',	0x6F : u'\x1E\xD3',
}
_e3e2 = {
	0x41 : u'\x1E\xA4', 0x45 : u'\x1E\xBE',	0x4F : u'\x1E\xD0',
	0x61 : u'\x1E\xA5', 0x65 : u'\x1E\xBF',	0x6F : u'\x1E\xD1',
}
_e3e4 = {
	0x41 : u'\x1E\xAA', 0x45 : u'\x1E\xC4',	0x4F : u'\x1E\xD6',
	0x61 : u'\x1E\xAB', 0x65 : u'\x1E\xC5',	0x6F : u'\x1E\xD7',
}
_e3f2 = {
	0x41 : u'\x1E\xAC', 0x45 : u'\x1E\xC6',	0x4F : u'\x1E\xD8',
	0x61 : u'\x1E\xAD', 0x65 : u'\x1E\xC7',	0x6F : u'\x1E\xD9',
}
_e4 = { 
	0x41 : u'\xC3',     0x45 : u'\x1E\xBC',	0x49 : u'\x01\x28',
	0x4E : u'\xD1',     0x4F : u'\xD5',	0x55 : u'\x01\x68',
	0x56 : u'\x1E\x7C', 0x59 : u'\x1E\xF8',	0x61 : u'\xE3',
	0x65 : u'\x1E\xBD', 0x69 : u'\x01\x29',	0x6E : u'\xF1',
	0x6F : u'\xF5',     0x75 : u'\x01\x69',	0x76 : u'\x1E\x7D',
	0x79 : u'\x1E\xF9',
}
_e4e2 = {
	0x4F : u'\x1E\x4C', 0x55 : u'\x1E\x78',	0x6F : u'\x1E\x4D',
	0x75 : u'\x1E\x79',
}
_e4e3 = {
	0x41 : u'\x1E\xAA', 0x45 : u'\x1E\xC4',	0x4F : u'\x1E\xD6',
	0x61 : u'\x1E\xAB', 0x65 : u'\x1E\xC5',	0x6F : u'\x1E\xD7',
}
_e4e6 = {
	0x41 : u'\x1E\xB4', 0x61 : u'\x1E\xB5',
}
_e4e8 = {
	0x4F : u'\x1E\x4E', 0x6F : u'\x1E\x4F',
}
_e5 = { 
	0x41 : u'\x01\x00', 0x45 : u'\x01\x12', 0x47 : u'\x1E\x20',	
	0x49 : u'\x01\x2A', 0x4F : u'\x01\x4C',	0x55 : u'\x01\x6A',
	0x61 : u'\x01\x01', 0x65 : u'\x01\x13',	0x67 : u'\x1E\x21',
	0x69 : u'\x01\x2B', 0x6F : u'\x01\x4D',	0x75 : u'\x01\x6B',
	0xA5 : u'\x01\xE2', 0xB5 : u'\x01\xE3',
}
_e5e1 = {
	0x45 : u'\x1E\x14', 0x4F : u'\x1E\x50',	0x65 : u'\x1E\x15',
	0x6F : u'\x1E\x51',
}
_e5e2 = {
	0x45 : u'\x1E\x16', 0x4F : u'\x1E\x52',	0x65 : u'\x1E\x17',
	0x6F : u'\x1E\x53',
}
_e5e7 = {
	0x41 : u'\x01\xE0', 0x61 : u'\x01\xE1',
}
_e5e8 = {
	0x41 : u'\x01\xDE', 0x55 : u'\x1E\x7A',	0x61 : u'\x01\xDF',
	0x75 : u'\x1E\x7B',
}
_e5f1 = {
	0x4F : u'\x01\xEC', 0x6F : u'\x01\xED',
}
_e5f2 = {
	0x4C : u'\x1E\x38', 0x52 : u'\x1E\x5C',	0x6C : u'\x1E\x39',
	0x72 : u'\x1E\x5D',
}
_e6 = {
	0x41 : u'\x01\x02', 0x45 : u'\x01\x14',	0x47 : u'\x01\x1E',
	0x49 : u'\x01\x2C', 0x4F : u'\x01\x4E',	0x55 : u'\x01\x6C',
	0x61 : u'\x01\x03', 0x65 : u'\x01\x15',	0x67 : u'\x01\x1F',
	0x69 : u'\x01\x2D', 0x6F : u'\x01\x4F',	0x75 : u'\x01\x6D',
}

_e6e0 = {
	0x41 : u'\x1E\xB2', 0x61 : u'\x1E\xB3',
}
_e6e1 = {
	0x41 : u'\x1E\xB0', 0x61 : u'\x1E\xB1',
}
_e6e2 = {
	0x41 : u'\x1E\xAE', 0x61 : u'\x1E\xAF',
}
_e6e4 = {
	0x41 : u'\x1E\xB4', 0x61 : u'\x1E\xB5',
}
_e6f0 = {
	0x45 : u'\x1E\x1C', 0x65 : u'\x1E\x1D',
}
_e6f2 = {
	0x41 : u'\x1E\xB6', 0x61 : u'\x1E\xB7',
}
_e7 = {
	0x42 : u'\x1E\x02', 0x43 : u'\x01\x0A',	0x44 : u'\x1E\x0A',
	0x45 : u'\x01\x16', 0x46 : u'\x1E\x1E',	0x47 : u'\x01\x20',
	0x48 : u'\x1E\x22', 0x49 : u'\x01\x30',	0x4D : u'\x1E\x40',
	0x4E : u'\x1E\x44', 0x50 : u'\x1E\x56',	0x52 : u'\x1E\x58',
	0x53 : u'\x1E\x60', 0x54 : u'\x1E\x6A',	0x57 : u'\x1E\x86',
	0x58 : u'\x1E\x8A', 0x59 : u'\x1E\x8E',	0x5A : u'\x01\x7B',
	0x62 : u'\x1E\x03', 0x63 : u'\x01\x0B',	0x64 : u'\x1E\x0B',
	0x65 : u'\x01\x17', 0x66 : u'\x1E\x1F',	0x67 : u'\x01\x21',
	0x68 : u'\x1E\x23', 0x6D : u'\x1E\x41',	0x6E : u'\x1E\x45',
	0x70 : u'\x1E\x57', 0x72 : u'\x1E\x59',	0x73 : u'\x1E\x61',
	0x74 : u'\x1E\x6B', 0x77 : u'\x1E\x87',	0x78 : u'\x1E\x8B',
	0x79 : u'\x1E\x8F', 0x7A : u'\x01\x7C',
}

_e7e2 = {
	0x53 : u'\x1E\x64', 0x73 : u'\x1E\x65',
}
_e7e5 = {
	0x41 : u'\x01\xE0', 0x61 : u'\x01\xE1',
}
_e7e9 = {
	0x53 : u'\x1E\x66', 0x73 : u'\x1E\x67',
}
_e7f2 = {
	0x53 : u'\x1E\x68', 0x73 : u'\x1E\x69',
}
_e8 = {
	0x41 : u'\xC4',     0x45 : u'\xCB',	0x48 : u'\x1E\x26',
	0x49 : u'\xCF',	    0x4F : u'\xD6',	0x55 : u'\xDC',
	0x57 : u'\x1E\x84', 0x58 : u'\x1E\x8C',	0x59 : u'\x01\x78',
	0x61 : u'\xE4',     0x65 : u'\xEB',	0x68 : u'\x1E\x27',
	0x69 : u'\xEF',     0x6F : u'\xF6',	0x74 : u'\x1E\x97',
	0x75 : u'\xFC',	    0x77 : u'\x1E\x85',	0x78 : u'\x1E\x8D',
	0x79 : u'\xFF',
}
_e8e1 = {
	0x55 : u'\x01\xDB', 0x75 : u'\x01\xDC',
}
_e8e2 = {
	0x49 : u'\x1E\x2E', 0x55 : u'\x01\xD7',	0x69 : u'\x1E\x2F',
	0x75 : u'\x01\xD8',
}
_e8e4 = {
	0x4F : u'\x1E\x4E', 0x6F : u'\x1E\x4F',
}
_e8e5 = {
	0x41 : u'\x01\xDE', 0x55 : u'\x1E\x7A',	0x61 : u'\x01\xDF',
	0x75 : u'\x1E\x7B',
}
_e8e9 = {
	0x55 : u'\x01\xD9', 0x75 : u'\x01\xDA',
}
_e9 = {
	0x41 : u'\x01\xCD', 0x43 : u'\x01\x0C',	0x44 : u'\x01\x0E',
	0x45 : u'\x01\x1A', 0x47 : u'\x01\xE6',	0x49 : u'\x01\xCF',
	0x4B : u'\x01\xE8', 0x4C : u'\x01\x3D',	0x4E : u'\x01\x47',
	0x4F : u'\x01\xD1', 0x52 : u'\x01\x58',	0x53 : u'\x01\x60',
	0x54 : u'\x01\x64', 0x55 : u'\x01\xD3',	0x5A : u'\x01\x7D',
	0x61 : u'\x01\xCE', 0x63 : u'\x01\x0D',	0x64 : u'\x01\x0F',
	0x65 : u'\x01\x1B', 0x67 : u'\x01\xE7',	0x69 : u'\x01\xD0',
	0x6A : u'\x01\xF0', 0x6B : u'\x01\xE9',	0x6C : u'\x01\x3E',
	0x6E : u'\x01\x48', 0x6F : u'\x01\xD2',	0x72 : u'\x01\x59',
	0x73 : u'\x01\x61', 0x74 : u'\x01\x65',	0x75 : u'\x01\xD4',
	0x7A : u'\x01\x7E',
}
_e9e7 = {
	0x53 : u'\x1E\x66', 0x73 : u'\x1E\x67',
}
_e9e8 = {
	0x55 : u'\x01\xD9', 0x75 : u'\x01\xDA',
}
_ea = {
	0x41 : u'\xC5',     0x55 : u'\x01\x6E',	0x61 : u'\xE5',
	0x75 : u'\x01\x6F', 0x77 : u'\x1E\x98',	0x79 : u'\x1E\x99',
}
_eae2 = {
	0x41 : u'\x01\xFA', 0x61 : u'\x01\xFB',
}
_ee = {
	0x4F : u'\x01\x50', 0x55 : u'\x01\x70',	0x6F : u'\x01\x51',
	0x75 : u'\x01\x71',
}
_f0 = {
	0x43 : u'\xC7',     0x44 : u'\x1E\x10',	0x47 : u'\x01\x22',
	0x48 : u'\x1E\x28', 0x4B : u'\x01\x36',	0x4C : u'\x01\x3B',
	0x4E : u'\x01\x45', 0x52 : u'\x01\x56',	0x53 : u'\x01\x5E',
	0x54 : u'\x01\x62', 0x63 : u'\xE7',	0x64 : u'\x1E\x11',
	0x67 : u'\x01\x23', 0x68 : u'\x1E\x29',	0x6B : u'\x01\x37',
	0x6C : u'\x01\x3C', 0x6E : u'\x01\x46',	0x72 : u'\x01\x57',
	0x73 : u'\x01\x5F', 0x74 : u'\x01\x63',
}
_f0e2 = {
	0x43 : u'\x1E\x08', 0x63 : u'\x1E\x09',
}
_f0e6 = {
	0x45 : u'\x1E\x1C', 0x65 : u'\x1E\x1D',
}
_f1 = {
	0x41 : u'\x01\x04', 0x45 : u'\x01\x18',	0x49 : u'\x01\x2E',
	0x4F : u'\x01\xEA', 0x55 : u'\x01\x72',	0x61 : u'\x01\x05',
	0x65 : u'\x01\x19', 0x69 : u'\x01\x2F', 0x6F : u'\x01\xEB',
	0x75 : u'\x01\x73',
}
_f1e5 = {
	0x4F : u'\x01\xEC', 0x6F : u'\x01\xED',
}
_f2 = {
	0x41 : u'\x1E\xA0', 0x42 : u'\x1E\x04',	0x44 : u'\x1E\x0C',
	0x45 : u'\x1E\xB8', 0x48 : u'\x1E\x24',	0x49 : u'\x1E\xCA',
	0x4B : u'\x1E\x32', 0x4C : u'\x1E\x36',	0x4D : u'\x1E\x42',
	0x4E : u'\x1E\x46', 0x4F : u'\x1E\xCC',	0x52 : u'\x1E\x5A',
	0x53 : u'\x1E\x62', 0x54 : u'\x1E\x6C',	0x55 : u'\x1E\xE4',
	0x56 : u'\x1E\x7E', 0x57 : u'\x1E\x88',	0x59 : u'\x1E\xF4',
	0x5A : u'\x1E\x92', 0x61 : u'\x1E\xA1',	0x62 : u'\x1E\x05',
	0x64 : u'\x1E\x0D', 0x65 : u'\x1E\xB9',	0x68 : u'\x1E\x25',
	0x69 : u'\x1E\xCB', 0x6B : u'\x1E\x33',	0x6C : u'\x1E\x37',
	0x6D : u'\x1E\x43', 0x6E : u'\x1E\x47',	0x6F : u'\x1E\xCD',
	0x72 : u'\x1E\x5B', 0x73 : u'\x1E\x63',	0x74 : u'\x1E\x6D',
	0x75 : u'\x1E\xE5', 0x76 : u'\x1E\x7F',	0x77 : u'\x1E\x89',
	0x79 : u'\x1E\xF5', 0x7A : u'\x1E\x93',
}
_f2e3 = {
	0x41 : u'\x1E\xAC', 0x45 : u'\x1E\xC6',	0x4F : u'\x1E\xD8',
	0x61 : u'\x1E\xAD', 0x65 : u'\x1E\xC7',	0x6F : u'\x1E\xD9',
}
_f2e5 = {
	0x4C : u'\x1E\x38', 0x52 : u'\x1E\x5C',	0x6C : u'\x1E\x39',
	0x72 : u'\x1E\x5D',
}
_f2e6 = {
	0x41 : u'\x1E\xB6', 0x61 : u'\x1E\xB7',
}
_f2e7 = {
	0x53 : u'\x1E\x68', 0x73 : u'\x1E\x69',
}
_f3 = {
	0x55 : u'\x1E\x72', 0x75 : u'\x1E\x73',
}

_f4 = {
	0x41 : u'\x1E\x00', 0x61 : u'\x1E\x01',
}

_f6 = {
	0x42 : u'\x1E\x06', 0x44 : u'\x1E\x0E',	0x4B : u'\x1E\x34',
	0x4C : u'\x1E\x3A', 0x4E : u'\x1E\x48',	0x52 : u'\x1E\x5E',
	0x54 : u'\x1E\x6E', 0x5A : u'\x1E\x94',	0x62 : u'\x1E\x07',
	0x64 : u'\x1E\x0F', 0x68 : u'\x1E\x96',	0x6B : u'\x1E\x35',
	0x6C : u'\x1E\x3B', 0x6E : u'\x1E\x49',	0x72 : u'\x1E\x5F',
	0x74 : u'\x1E\x6F', 0x7A : u'\x1E\x95',
}

_f9 = {
	0x48 : u'\x1E\x2A', 0x68 : u'\x1E\x2B',
}

_s1 = {
	0xe0: _e0, 0xe1: _e1, 0xe2: _e2, 0xe3: _e3, 0xe4: _e4,	
	0xe5: _e5, 0xe6: _e6, 0xe7: _e7, 0xe8: _e8, 0xe9: _e9,	
	0xea: _ea, 0xee: _ee, 0xf0: _f0, 0xf1: _f1, 0xf2: _f2,
	0xf3: _f3, 0xf4: _f4, 0xf6: _f6, 0xf9: _f9,
}

def ansel_to_utf8(s):
    """Converts an ANSEL encoded string to UTF8"""

    buff = cStringIO.StringIO()
    while s:
        c0 = ord(s[0])
        if c0 <= 31:
            head = ' '
            s = s[1:]
        elif c0 > 127:
            try:
                if c0 >= 0xC0:
                    c1 = ord(s[1])
                    head = _s1[c0][c1]
                    s = s[2:]
                else:
                    head = _s0[c0]
                    s = s[1:]
            except Exception:
                head = s[0]
                s = s[1:]
        else:
            head = s[0]
            s = s[1:]
        buff.write(head)
    ans = buff.getvalue()
    buff.close()
    return ans
