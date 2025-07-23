import string
import random
import warnings

import pandas as pd
import numpy as np

from .data_wrangling import OrderFlowData
from .plot import OrderFlowPlot

warnings.filterwarnings('ignore')


class OrderFlowChart(
    OrderFlowData,
    OrderFlowPlot,
):
    """
    OrderFlowChart class for visualizing order flow data with OHLC data.
    It inherits from OrderFlowData for data processing and OrderFlowPlot for plotting.
    It takes in orderflow data and OHLC data, processes it, and provides methods to plot
    the order flow chart.
    """
    def __init__(self, orderflow_data, ohlc_data, identifier_col=None, imbalance_col=None, **kwargs):
        """
        The constructor for OrderFlowChart class.
        It takes in the orderflow data and the ohlc data and creates a unique identifier for each candle if not provided.
        It also calculates the imbalance if not provided.
        The data should have datetime index and should have the following columns:
        orderflow_data: ['bid_size', 'price', 'ask_size', 'identifier']
        ohlc_data: ['open', 'high', 'low', 'close', 'identifier']

        The identifier column is used to map the orderflow data to the ohlc data.
        """

        if 'data' in kwargs:
            self.use_processed_data(kwargs['data'])
        else:
            self.orderflow_data = orderflow_data
            self.ohlc_data = ohlc_data
            self.identifier_col = identifier_col
            self.imbalance_col = imbalance_col
            self.is_processed = False
            self.granularity = abs(self.orderflow_data.iloc[0]['price'] - self.orderflow_data.iloc[1]['price'])

    def create_identifier(self):
        """
        This method will generate a unique gibberish string for each candle based on the timestamp and the price.
        """
        letters = string.ascii_letters
        identifier = [ ''.join(random.choice(letters) for _ in range(5)) for i in range(self.ohlc_data.shape[0]) ]
        self.ohlc_data['identifier'] = identifier
        self.orderflow_data.loc[:, 'identifier'] = self.ohlc_data['identifier']

    def create_sequence(self):
        """
        This method will create a sequence column in the ohlc_data and orderflow_data based on the identifier column.
        """
        self.ohlc_data['sequence'] = self.ohlc_data[self.identifier_col].str.len()
        self.orderflow_data['sequence'] = self.orderflow_data[self.identifier_col].str.len()

    def calc_imbalance(self, df):
        """
        This method will calculate the imbalance for the orderflow data.
        It will create a new column 'size' which is the difference between the bid size and the ask size.
        """
        df['sum'] = df['bid_size'] + df['ask_size']
        df['time'] = df.index.astype(str)
        bids, asks = [], []
        for b, a in zip(df['bid_size'].astype(int).astype(str),
                        df['ask_size'].astype(int).astype(str)):
            dif = 4 - len(a)
            a = a + (' ' * dif)
            dif = 4 - len(b)
            b = (' ' * dif) + b
            bids.append(b)
            asks.append(a)

        df['text'] = pd.Series(bids, index=df.index) + '  ' + \
            pd.Series(asks, index=df.index)
        df.index = df['identifier']

        if self.imbalance_col is None:
            print("Calculating imbalance, as no imbalance column was provided.")
            df['size'] = (df['bid_size'] - df['ask_size'].shift().bfill()) / \
                (df['bid_size'] + df['ask_size'].shift().bfill())
            df['size'] = df['size'].ffill().bfill()
        else:
            print("Using imbalance column: {}".format(self.imbalance_col))
            df['size'] = df[self.imbalance_col]
            df = df.drop([self.imbalance_col], axis=1)
        # df = df.drop(['bid_size', 'ask_size'], axis=1)
        return df

    def annotate(self, df2):
        """
        This method will annotate the orderflow data with the sum of bid and ask sizes.
        It will create a new column 'text' which is a string of █ characters based on the sum of bid and ask sizes.
        """
        df2 = df2.drop(['size'], axis=1)
        df2['sum'] = df2['sum'] / df2.groupby(df2.index)['sum'].transform('max')
        df2['text'] = ''
        df2['time'] = df2['time'].astype(str)
        df2['text'] = ['█' * int(sum_ * 10) for sum_ in df2['sum']]
        df2['text'] = '                    ' + df2['text']
        df2['time'] = df2['time'].astype(str)
        return df2

    def range_proc(self, ohlc, type_='hl'):
        """
        This method will process the ohlc data to create a sequence of high and low prices
        or open and close prices based on the type parameter.
        It will create a new dataframe with the following columns:
        - price: the high or low or open or close price
        - identifier: the identifier of the candle
        - sequence: the sequence number of the candle
        - time: the timestamp of the candle
        """
        if type_ == 'hl':
            seq = pd.concat([ohlc['low'], ohlc['high']])
        if type_ == 'oc':
            seq = pd.concat([ohlc['open'], ohlc['close']])
        id_seq = pd.concat([ohlc['identifier'], ohlc['identifier']])
        seq_hl = pd.concat([ohlc['sequence'], ohlc['sequence']])
        seq = pd.DataFrame(seq, columns=['price'])
        seq['identifier'] = id_seq
        seq['sequence'] = seq_hl
        seq['time'] = seq.index
        seq = seq.sort_index()
        seq = seq.set_index('identifier')
        return seq

    def candle_proc(self, df):
        """
        This method will process the dataframe to create a sequence of candles.
        It will create a new dataframe with the following columns:
        - price: the price of the candle
        - identifier: the identifier of the candle
        - sequence: the sequence number of the candle
        """
        df = df.sort_values(by=['time', 'sequence', 'price'])
        df = df.reset_index()
        df_dp = df.iloc[1::2].copy()
        df = pd.concat([df, df_dp])
        df = df.sort_index()
        df = df.set_index('identifier')
        df = df.sort_values(by=['time', 'sequence'])
        # df = df.sort_index()
        df[2::3] = np.nan
        return df

    def calc_params(self, of, ohlc):
        """
        This method will calculate the delta, cumulative delta, rate of change and volume for the orderflow data.
        It will create a new dataframe with the following columns:
        - value: the value of the delta, cumulative delta, rate of change or volume
        - type: the type of the value (delta, cum_delta, roc, volume)
        - text: the text representation of the value
        """
        delta = of.groupby(of['identifier']).sum()['ask_size'] - \
            of.groupby(of['identifier']).sum()['bid_size']
        delta = delta[ohlc['identifier']]
        cum_delta = delta.rolling(10).sum()
        roc = cum_delta.diff()/cum_delta.shift(1) * 100
        roc = roc.fillna(0).round(2)
        volume = of.groupby(of['identifier']).sum()['ask_size'] + of.groupby(of['identifier']).sum()['bid_size']
        delta = pd.DataFrame(delta, columns=['value'])
        delta['type'] = 'delta'
        cum_delta = pd.DataFrame(cum_delta, columns=['value'])
        cum_delta['type'] = 'cum_delta'
        roc = pd.DataFrame(roc, columns=['value'])
        roc['type'] = 'roc'
        volume = pd.DataFrame(volume, columns=['value'])
        volume['type'] = 'volume'

        labels = pd.concat([delta, cum_delta, roc, volume])
        labels = labels.sort_index()
        labels['text'] = labels['value'].astype(str)

        labels['value'] = np.tanh(labels['value'])
        # raise Exception
        return labels

    def plot_ranges(self, ohlc):
        """
        This method will calculate the ranges for the plot.
        It will return the ymin, ymax, xmin, xmax, tickvals and ticktext for the plot.
        """
        ymin = ohlc['high'][-1] + 1
        ymax = ymin - int(48*self.granularity)
        xmax = ohlc.shape[0]
        xmin = xmax - 9
        tickvals = [i for i in ohlc['identifier']]
        ticktext = [i for i in ohlc.index]
        return ymin, ymax, xmin, xmax, tickvals, ticktext
