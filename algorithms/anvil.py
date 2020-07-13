from .huffman import Huffman
from .lz77 import Lz77


class Anvil:
    def __new__(cls): pass
    
    @staticmethod
    def encode(file_path: str, save_path: str):
        try:
            Lz77.encode(file_path, save_path)
        except Exception as e:
            raise Exception(f'error in lz77 encode: {e}')
        
        try:
            Huffman.encode(save_path, save_path)
        except Exception as e:
            raise Exception(f'error in huffman encode: {e}')
    
    @staticmethod
    def decode(file_path: str, save_path: str):
        try:
            Huffman.decode(file_path, save_path)
        except Exception as e:
            raise Exception(f'error in huffman decode: {e}')
        
        try:
            Lz77.decode(save_path, save_path)
        except Exception as e:
            raise Exception(f'error in lz77 decode: {e}')
