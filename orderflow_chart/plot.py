import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.graph_objs import *


class OrderFlowPlot():
    def plot(self, return_figure=False):
        """
        This method will plot the order flow chart using the processed data.
        It will create a figure with two subplots: one for the order flow data and one for the OHLC data.
        It will also add traces for the order flow data, OHLC data, and the imbalance.
        The order flow data will be plotted as a heatmap, the OHLC data will be plotted as candlesticks,
        and the imbalance will be plotted as a line chart.
        The figure will be returned if return_figure is True, otherwise it will be shown.
        """
        if not self.is_processed:
            self.process_data()

        ymin, ymax, xmin, xmax, tickvals, ticktext = self.plot_ranges(self.ohlc_data)
        print("Total candles: ", self.ohlc_data.shape[0])
        # Create figure
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=0.0, row_heights=[9, 1])

        fig.add_trace(go.Scatter(x=self.df2['identifier'], y=self.df2['price'], text=self.df2['text'],
                                name='VolumeProfile', textposition='middle right',
                                textfont=dict(size=8, color='rgb(0, 0, 255, 0.0)'), hoverinfo='none',
                                mode='text', showlegend=True,
                                marker=dict(
                                sizemode='area',
                                sizeref=0.1,  # Adjust the size scaling factor as needed
                                )), row=1, col=1)

        # Add trace for orderflow data
        fig.add_trace(
            go.Heatmap(
                x=self.df['identifier'],
                y=self.df['price'],
                z=self.df['size'],
                text=self.df['text'],
                colorscale='icefire_r',
                showscale=False,
                showlegend=True,
                name='BidAsk',
                texttemplate="%{text}",
                textfont={
                    "size": 11,
                    "family": "Courier New"},
                hovertemplate="Price: %{y}<br>Size: %{text}<br>Imbalance: %{z}<extra></extra>",
                xgap=60),
            row=1,
            col=1)

        fig.add_trace(
            go.Scatter(
                x=self.green_hl.index,
                y=self.green_hl['price'],
                name='Candle',
                legendgroup='group',
                showlegend=True,
                line=dict(
                    color='green',
                    width=1.5)),
            row=1,
            col=1)

        fig.add_trace(
            go.Scatter(
                x=self.red_hl.index,
                y=self.red_hl['price'],
                name='Candle',
                legendgroup='group',
                showlegend=False,
                line=dict(
                    color='red',
                    width=1.5)),
            row=1,
            col=1)

        fig.add_trace(
            go.Scatter(
                x=self.green_oc.index,
                y=self.green_oc['price'],
                name='Candle',
                legendgroup='group',
                showlegend=False,
                line=dict(
                    color='green',
                    width=6)),
            row=1,
            col=1)

        fig.add_trace(
            go.Scatter(
                x=self.red_oc.index,
                y=self.red_oc['price'],
                name='Candle',
                legendgroup='group',
                showlegend=False,
                line=dict(
                    color='red',
                    width=6)),
            row=1,
            col=1)

        # fig.add_trace(go.Scatter(x=buy_vwap.index, y=buy_vwap, name='VWAP', legendgroup='group', showlegend=True, line=dict(color='green', width=1.5)), row=1, col=1)

        # fig.add_trace(go.Scatter(x=sell_vwap.index, y=sell_vwap, name='VWAP', legendgroup='group', showlegend=False, line=dict(color='red', width=1.5)), row=1, col=1)

        fig.add_trace(
            go.Heatmap(
                x=self.labels.index,
                y=self.labels['type'],
                z=self.labels['value'],
                colorscale='rdylgn',
                showscale=False,
                showlegend=True,
                name='Parameters',
                text=self.labels['text'],
                texttemplate="%{text}",
                textfont={
                    "size": 10},
                hovertemplate="%{x}<br>%{text}<extra></extra>",
                xgap=4,
                ygap=4),
            row=2,
            col=1)

        fig.update_layout(title='Order Book Chart',
                        yaxis=dict(title='Price', showgrid=False, range=[
                                    ymax, ymin], tickformat='.2f'),
                        yaxis2=dict(fixedrange=True, showgrid=False),
                        xaxis2=dict(title='Time', showgrid=False),
                        xaxis=dict(showgrid=False, range=[xmin, xmax]),
                        height=780,
                        template='plotly_dark',
                        paper_bgcolor='#222', plot_bgcolor='#222',
                        dragmode='pan', margin=dict(l=10, r=0, t=40, b=20),)

        fig.update_xaxes(
            showspikes=True,
            spikecolor="white",
            spikesnap="cursor",
            spikemode="across",
            spikethickness=0.25,
            tickmode='array',
            tickvals=tickvals,
            ticktext=ticktext)
        fig.update_yaxes(
            showspikes=True,
            spikecolor="white",
            spikesnap="cursor",
            spikemode="across",
            spikethickness=0.25)
        fig.update_layout(spikedistance=1000, hoverdistance=100)

        config = {
            'modeBarButtonsToRemove': ['zoomIn', 'zoomOut', 'zoom', 'autoScale'],
            'scrollZoom': True,
            'displaylogo': False,
            'modeBarButtonsToAdd': ['drawline',
                                    'drawopenpath',
                                    'drawclosedpath',
                                    'drawcircle',
                                    'drawrect',
                                    'eraseshape'
                                    ]
        }

        if return_figure:
            return fig

        # Show figure
        fig.show(config=config)
