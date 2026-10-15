def may_start(runs, published_sequence):
    return all(r["sequence"] <= published_sequence or r["status"] == "abandoned" for r in runs)


def may_abandon(run, published_sequence):
    return run["sequence"] > published_sequence
