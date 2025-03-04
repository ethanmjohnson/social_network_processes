# this contains the function to discover a petri net


def discover_pn(log):

    # discover petri net
    print('discovering...')
    net, im, fm = pm4py.discover_petri_net_inductive(log)
    
    if fm is None:
        fm = {}

    return (net, im, fm)


if __name__ == "__main__":
    import pm4py
    from pm4py.objects.log.importer.xes import importer as xes_importer
    from pathlib import Path
    from pm4py.visualization.petri_net import visualizer as pn_viz

    variant = xes_importer.Variants.ITERPARSE
    parameters = {variant.value.Parameters.TIMESTAMP_SORT: True}
    log = xes_importer.apply(str(Path(__file__).parent.parent.parent / "data/processed/honduras_coordinated_log.xes"), variant=variant, parameters=parameters)

    # discover pn
    net, im, fm = discover_pn(log)

    # save pn

    pm4py.write_pnml(net, im, fm, str(Path(__file__).parent.parent.parent / "models/honduras_coordinated.pnml"))

    # visualise pn

    gviz = pn_viz.apply(net, im, fm)

    # save pn image

    pn_viz.save(gviz, Path(__file__).parent.parent.parent / "figures/honduras_coordinated.png")


    # to read petri for future 
    # pn2, im2, fm2 = pm4py.read_pnml(path)
