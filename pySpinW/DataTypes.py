import numpy as np

class DataTypes:

    def __init__(self, matlab):
        """
        Data Converter to/from python and MATLAB
        :param matlab:
        """
        self.matlab = matlab
        # self.outNumpy = True
        # self.transpose = True

    def encode(self, data):

        # What is data?
        # 1) If it's a numpy array or a list, we convert. to matlab.double
        # 2) If it is a dict, then we enumerate values and encode them.
        # 3) If it's a tuple, it's a cell, which we enumerate. BUT, then we convert it into a list.
        # 4) If it is a double it's a double, if a integer, we encode to a double as well. MATLAB is tricky :-/

        if isinstance(data, (list, np.ndarray)):
            # Case 1)
            if isinstance(data, np.ndarray):
                data = data.tolist()
            data = self.matlab.double(data)
        elif isinstance(data, np.integer):
            # Case 4)
            data = float(data)
        else:
            # Case 2, 3
            if isinstance(data, dict):
                # Case 2)
                for key, item in data.items():
                    data[key] = self.encode(item)
            elif isinstance(data, tuple):
                # Case 3)
                newdata = []
                for item in data:
                    newdata.append(self.encode(item))
                data = newdata

        # Unknown data i.e. text should pass through
        # TODO Make sure this works for more data cases...
        return data

    def decode(self, data):
        raise NotImplementedError