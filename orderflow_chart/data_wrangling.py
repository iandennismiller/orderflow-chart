import pandas as pd
import numpy as np


class OrderFlowData():
    def process_data(self):
        if self.identifier_col is None:
            self.identifier_col = 'identifier'
            self.create_identifier()

        self.create_sequence()

        self.df = self.calc_imbalance(self.orderflow_data)

        self.df2 = self.annotate(self.df.copy())

        self.green_id = self.ohlc_data.loc[self.ohlc_data['close'] >= self.ohlc_data['open']]['identifier']
        self.red_id = self.ohlc_data.loc[self.ohlc_data['close'] < self.ohlc_data['open']]['identifier']

        self.high_low = self.range_proc(self.ohlc_data, type_='hl')
        self.green_hl = self.high_low.loc[self.green_id]
        self.green_hl = self.candle_proc(self.green_hl)

        self.red_hl = self.high_low.loc[self.red_id]
        self.red_hl = self.candle_proc(self.red_hl)

        self.open_close = self.range_proc(self.ohlc_data, type_='oc')

        self.green_oc = self.open_close.loc[self.green_id]
        self.green_oc = self.candle_proc(self.green_oc)

        self.red_oc = self.open_close.loc[self.red_id]
        self.red_oc = self.candle_proc(self.red_oc)

        self.labels = self.calc_params(self.orderflow_data, self.ohlc_data)

        self.is_processed = True

    def get_processed_data(self):
        """
        This method will return the processed data as a dictionary.
        It will include the orderflow data, labels, green and red high-low and open-close
        sequences, and the original OHLC data.
        """
        if not self.is_processed:
            try:
                self.process_data()
            except Exception as e:
                raise Exception("Data processing failed. Please check the data types and the structure of the data. Refer to documentation for more information.")

        datas = [self.df, self.labels, self.green_hl, self.red_hl, self.green_oc, self.red_oc, self.df2, self.ohlc_data]
        datas2 = []
        # Convert all timestamps to utc float
        temp = ''
        for data in datas:
            temp = data.copy()
            temp.index.name = 'index'
            try:
                temp = temp.reset_index()
            except Exception as e:
                pass
            dtype_dict = {i:str(j) for i, j in temp.dtypes.items()}
            temp = temp.astype('str')
            temp = temp.fillna('nan')
            temp = temp.to_dict(orient='list')
            temp['dtypes'] = dtype_dict
            datas2.append(temp)

        out_dict = {
            'orderflow': datas2[0],
            'labels': datas2[1],
            'green_hl': datas2[2],
            'red_hl': datas2[3],
            'green_oc': datas2[4],
            'red_oc': datas2[5],
            'orderflow2': datas2[6],
            'ohlc': datas2[7]
        }

        return out_dict

    @classmethod
    def from_preprocessed_data(cls, data):
        """
        This class method will create an instance of OrderFlowChart from preprocessed data.
        It expects a dictionary with keys 'orderflow', 'labels', 'green_hl', 'red_hl',
        'green_oc', 'red_oc', 'orderflow2', and 'ohlc'.
        """
        self = cls(None, None, data=data)
        return self

    def use_processed_data(self, data):
        """
        This method will use the preprocessed data to set the instance variables.
        It expects a dictionary with keys 'orderflow', 'labels', 'green_hl', 'red_hl',
        'green_oc', 'red_oc', 'orderflow2', and 'ohlc'.
        """
        # pop the dtypes
        dtypes = data['orderflow'].pop('dtypes')
        self.df = pd.DataFrame(data['orderflow']).replace('nan', np.nan)
        self.df = self.df.astype(dtypes)
        try:
            self.df = self.df.set_index('index')
        except Exception as e:
            pass

        dtypes = data['labels'].pop('dtypes')
        self.labels = pd.DataFrame(data['labels']).replace('nan', np.nan)
        self.labels = self.labels.astype(dtypes)
        try:
            self.labels = self.labels.set_index('index')
        except Exception as e:
            pass

        dtypes = data['green_hl'].pop('dtypes')
        self.green_hl = pd.DataFrame(data['green_hl']).replace('nan', np.nan)
        self.green_hl = self.green_hl.astype(dtypes)
        try:
            self.green_hl = self.green_hl.set_index('index')
        except Exception as e:
            pass

        dtypes = data['red_hl'].pop('dtypes')
        self.red_hl = pd.DataFrame(data['red_hl']).replace('nan', np.nan)
        self.red_hl = self.red_hl.astype(dtypes)
        try:
            self.red_hl = self.red_hl.set_index('index')
        except Exception as e:
            pass

        dtypes = data['green_oc'].pop('dtypes')
        self.green_oc = pd.DataFrame(data['green_oc']).replace('nan', np.nan)
        self.green_oc = self.green_oc.astype(dtypes)
        try:
            self.green_oc = self.green_oc.set_index('index')
        except Exception as e:
            pass

        dtypes = data['red_oc'].pop('dtypes')
        self.red_oc = pd.DataFrame(data['red_oc']).replace('nan', np.nan)
        self.red_oc = self.red_oc.astype(dtypes)
        try:
            self.red_oc = self.red_oc.set_index('index')
        except Exception as e:
            pass

        dtypes = data['orderflow2'].pop('dtypes')
        self.df2 = pd.DataFrame(data['orderflow2']).replace('nan', np.nan)
        self.df2 = self.df2.astype(dtypes)
        try:
            self.df2 = self.df2.set_index('index')
        except Exception as e:
            pass

        dtypes = data['ohlc'].pop('dtypes')
        self.ohlc_data = pd.DataFrame(data['ohlc']).replace('nan', np.nan)
        self.ohlc_data = self.ohlc_data.astype(dtypes)
        try:
            self.ohlc_data = self.ohlc_data.set_index('index')
        except Exception as e:
            pass
        self.granularity = abs(self.df.iloc[0]['price'] - self.df.iloc[1]['price'])
        self.is_processed = True

