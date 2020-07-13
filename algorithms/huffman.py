from typing import Dict, List
from math import ceil


class _Node:
    def __init__(self, left=None, right=None, freq=None, char=None):
        self.left = left
        self.right = right
        self.char = char

        if freq is None:
            self.freq = left.freq + right.freq
        else:
            self.freq = freq

    def is_leaf(self) -> bool:
        return self.char is not None

    def huffman_codes(self, inherited_bitstring: str = '') -> Dict[int, str]:
        if self.is_leaf():
            # if the inherited code is empty (if a code wasn't inherited from
            # parent to leaf node) set huffman code to default (0)
            return {self.char: inherited_bitstring if inherited_bitstring else '0'}

        codes: Dict[int, str] = {}

        # update inherited code and inherit to the next nodes
        # then add all values returned from child nodes to the map
        codes.update(self.left.huffman_codes(inherited_bitstring + '0'))
        codes.update(self.right.huffman_codes(inherited_bitstring + '1'))

        return codes


class Huffman:
    def __new__(cls): pass

    @staticmethod
    def _file_freq_dict(file_path: str) -> Dict[int, int]:
        freq_dict: Dict[int, int] = {}
        
        with open(file_path, 'rb') as file:
            while True:
                char = file.read(1)
                
                # if the file ends, stop reading
                if not char:
                    break
                
                byte = ord(char)
                
                # if the dict contains the char, increase the number of the chars
                if byte in freq_dict.keys():
                    freq_dict[byte] += 1
                # if the map don't contains the char, add char to the map
                else:
                    freq_dict[byte] = 1
            
        return freq_dict

    @staticmethod
    def _build_tree(node_list: List[_Node]) -> _Node:
        # function will be used as parameter for min function
        # while getting the node that has min frequency
        def get_freq(node): return node.freq

        # continue until one root node remains
        while len(node_list) > 1:
            # get 2 nodes that has min freq and remove them from the list
            left_node = min(node_list, key=get_freq)
            node_list.remove(left_node)

            right_node = min(node_list, key=get_freq)
            node_list.remove(right_node)

            # create a parent node that contains these nodes as child nodes
            parent_node = _Node(
                left=left_node,
                right=right_node,
            )

            # add parent node to the list
            node_list.append(parent_node)

        # get remaining node that contains other nodes as child
        return node_list[0]

    @staticmethod
    def _normalize_freq_dict(freq_dict: Dict[int, int]) -> Dict[int, int]:
        # apply the max function every freq pair and get the max freq
        max_freq = max(freq_dict.values())

        normalized_freq_dict = {}

        for char, freq in freq_dict.items():
            # normalize freq from (0, x) to (0, 255)
            # so it can be written as one byte to file
            normalized_freq_dict[char] = ceil(freq * 255 / max_freq)

        return normalized_freq_dict

    @staticmethod
    def _dict_to_node_list(dict_: Dict[int, int]) -> List[_Node]:
        node_list: List[_Node] = []
        
        # create a _Node object for every char/freq pair
        for char, freq in dict_.items():
            node = _Node(char=char, freq=freq)
            node_list.append(node)

        return node_list

    @staticmethod
    def encode(file_path: str, save_path: str):
        # read file and get freq of the chars
        freq_dict = Huffman._file_freq_dict(file_path)

        # normalize frequencies so it can be written as one byte to file
        freq_dict = Huffman._normalize_freq_dict(freq_dict)

        # create an node list from frequency map
        leaf_nodes = Huffman._dict_to_node_list(freq_dict)

        # build huffman tree for creating unique binary codes
        huffman_tree = Huffman._build_tree(leaf_nodes)

        # get binary code of each charcode (example: {100: '10110', 132: '0', ...})
        huffman_codes = huffman_tree.huffman_codes()

        encoded_bytes = bytearray()

        # write freq dict for creating huffman tree when it will be decoded
        # (example: freq0, char0, freq1, char1, freq2, ...)
        for char, freq in freq_dict.items():
            encoded_bytes.append(freq)
            encoded_bytes.append(char)

        # 0 freq is the sign for the end of the freq dict
        encoded_bytes.append(0)
        
        with open(file_path, 'rb') as file:
            buffer: List[str] = []

            while True:
                char = file.read(1)
                
                if not char:
                    break
                
                byte = ord(char)
                
                # get the huffman code of the char from the freq dict
                huffman_code = huffman_codes[byte]

                # add all bits of the huffman code to the buffer
                for bit in huffman_code:
                    buffer.append(bit)

                # if size of the buffer reaches to a byte
                while len(buffer) >= 8:
                    # get the first 8 elements and concat them
                    byte_string = ''.join(buffer[:8])

                    # parse the string to int and add to the list
                    encoded_byte = int(byte_string, 2)
                    encoded_bytes.append(encoded_byte)

                    # remove first 8 elements from list
                    buffer = buffer[8:]

            if buffer == []:
                # if buffer is empty, all bits in the last byte must be used
                used_bits_in_last_byte = 8
            else:
                # if buffer is not empty, used bits in the last byte
                # must be equal to the length of the buffer
                used_bits_in_last_byte = len(buffer)

                # add the last remaining byte to the list
                byte_string = ''.join(buffer)

                encoded_byte = int(byte_string, 2)
                encoded_bytes.append(byte)

            # add the number of the used bits in the last byte to the encoded_bytes
            # so decoder can distinguish unused bits in the last byte
            encoded_bytes.append(used_bits_in_last_byte)
            
            with open(save_path, 'wb') as save:
                # write all encoded_bytes to the file
                save.write(encoded_bytes)

    @staticmethod
    def decode(file_path: str, save_path: str):
        reading_freq_dict = True
        freq_dict: Dict[int, int] = {}
        is_freq = True
        last_freq: int

        huffman_codes: Dict[str, int] = {}
        bitstring_list: List[int] = []

        with open(file_path, 'rb') as file:
            while True:
                char = file.read(1)
                
                if not char:
                    break
                
                byte = ord(char)

                # when reading freq dict
                if reading_freq_dict:

                    # if current byte represents a freq
                    if is_freq:

                        # if freq is 0 (end sign for freq dict)
                        if byte == 0:
                            # create a list of nodes from freq dict
                            leaf_nodes = Huffman._dict_to_node_list(freq_dict)

                            # build a huffman tree from leaf nodes
                            huffman_tree = Huffman._build_tree(leaf_nodes)

                            # add the huffman codes as a pair of
                            # (code-char) to the dict
                            for char, binary in huffman_tree.huffman_codes().items():
                                huffman_codes[binary] = char

                            # finish reading freq dict
                            reading_freq_dict = False

                        # if reading freq dict is not finished
                        else:
                            last_freq = byte

                    # if current byte represents a char
                    else:
                        freq_dict[byte] = last_freq

                    # if current byte represents freq, set is_freq to false
                    # for next byte, otherwise vice versa
                    is_freq = not is_freq

                # when reading huffman codes of chars
                else:
                    # add encoded byte to the list in bit-string format
                    bitstring_list.append('{0:08b}'.format(byte))

        # last byte in the file represents the number of
        # the used bits in the last but two byte
        used_bits_in_last_byte = int(bitstring_list.pop(), 2)

        # the last but two byte has bits that may not be used, encoder wrote a byte
        # to the end of the file to specify the used bytes
        last_byte = bitstring_list.pop()[-used_bits_in_last_byte:]
        bitstring_list.append(last_byte)

        decoded_bytes = bytearray()
        key_buffer = ''
        
        for bitstring in bitstring_list:    
            for bit in bitstring:
                # add current bit to the buffer
                key_buffer += bit

                # if there is huffman code that matches with key_buffer
                if key_buffer in huffman_codes.keys():
                    # add corresponding charcode to the decoded bytes
                    decoded_bytes.append(huffman_codes[key_buffer])

                    # reset buffer
                    key_buffer = ''

        with open(save_path, 'wb') as save:
            # write all decoded bytes to the file
            save.write(decoded_bytes)


class Lz77:
    def __new__(cls): pass

    @staticmethod
    def encode(file_path: str, save_path: str):
        with open(file_path, 'rb') as file:
            bytes_ = file.read()
            encoded_bytes = bytearray()

            # index
            i = 0
            while i < len(bytes_):
                # distance between current index and matched pointer
                match_distance = 0

                # length of the matched pointer
                match_length = 0

                # search index
                for j in range(max(0, i - 255), i):
                    # the lookahead index for continues byte group
                    k = 0

                    # conditions for increasing the lookahead index
                    while all([
                        # the lookahead index musn't be greater than
                        # the number of byte after i, so decoder won't
                        #  give an index error
                        (k < len(bytes_) - i - 1),

                        # lookahead index musn't be greater than 255,
                        # so it can fit in one byte
                        (k < 256),

                        # sum of the lookahead index and the search index
                        # musn't be greater than current index, so decoder
                        # won't try to access not loaded byte
                        # after current index
                        (j + k < i),

                        # look after the current index and the search index,
                        # they must be same
                        (bytes_[i + k] == bytes_[j + k]),
                    ]):
                        # +1 -> indexes starts from 0, lengths starts from 1
                        length = k + 1

                        # distance -> current index - search index
                        distance = i - j

                        # get pointer that has max length
                        if (length >= match_length):
                            match_length = length
                            match_distance = distance

                        k += 1

                # increase index by length of the matched byte
                i += match_length

                # get the next byte from byte
                next_byte = bytes_[i]

                # add the distance, length and next byte to the list
                encoded_bytes.append(match_distance)
                encoded_bytes.append(match_length)
                encoded_bytes.append(next_byte)

                i += 1
        
        with open(save_path, 'wb') as save:
            save.write(encoded_bytes)

    @staticmethod
    def decode(file_path: str, save_path: str):
        with open(file_path, 'rb') as file:
            decoded_bytes = bytearray()
            
            while True:
                bytes_ = file.read(3)
                
                # if the file ends, stop reading
                if not bytes_:
                    break
                
                # get distance, length and next byte from
                # the file in the fixed order
                distance, length, next_byte = bytes_
                
                # if it is a pointer to the past byte
                if (distance != 0):
                    # the start of the byte
                    start = len(decoded_bytes) - distance

                    # skip to the `start` and take the first `length` byte
                    bytes_ = decoded_bytes[start: start + length]

                    decoded_bytes.extend(bytes_)

                # add next byte to the list
                decoded_bytes.append(next_byte)
        
        with open(save_path, 'wb') as save:
            save.write(decoded_bytes)

