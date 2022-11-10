import pandapipes as pp
import pandas as pd
import example
import pandapipes.plotting as plot

net = example.pipe_square_flat(fluid="lgas", p_junction=1.05, tfluid_K=293.15, pipe_d=0.3, pipe_l=1)
#plot.simple_plot(net, pipe_width=2.0, junction_size=1.0, plot_sinks=True, plot_sources=True, sink_size=1.0, source_size=1.0, show_plot=True)

d = {'a': 1, 'b': 2, 'c': 3}
ser = pd.Series(data=d, index=['a', 'b', 'c'])

junction_to = net.pipe.groupby(['to_junction']).size()


for index, i in junction_to.iteritems():
#for i, number in junction_to.iteritems():
    print(i)
    #print(junction_to.values[i])
    #if 2 == junction_to.values[i]:
    #    geodata = net.junction_geodata.loc[net.junction_geodata.index[i]]