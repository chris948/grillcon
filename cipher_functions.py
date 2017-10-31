#!/usr/bin/python
import base64


class CipherFunctions:
    def __init__(self, key_file):
        # CP 12-29-16 moving key to a different file
        with open(key_file, 'r') as f:
            # Get the entire contents of the file
            self.key = f.read()

        # Remove any whitespace at the end, e.g. a newline
        self.key = self.key.strip()

    def encode(self, clear):
        """

        :rtype: string
        """
        enc = []
        for i in range(len(clear)):
            key_c = self.key[i % len(self.key)]
            enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
            enc.append(enc_c)
        return base64.urlsafe_b64encode("".join(enc))

    def decode(self, enc):
        dec = []
        enc = base64.urlsafe_b64decode(enc)
        for i in range(len(enc)):
            key_c = self.key[i % len(self.key)]
            dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
            dec.append(dec_c)
        return "".join(dec)
