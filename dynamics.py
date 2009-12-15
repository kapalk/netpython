"""Methods for dynamic network."""

from collections import deque

def eventBetweenness(events, events_reversed=None, nodeBetweenness=None,
                     include_path_ends=False):
    """Calculate the event betweenness of all events.

    The event betweenness is defined as the total number of
    time-respecting paths that go through an event.

    Parameters
    ----------
    events : sequence of tuples (int, int, int)
        A sequence of events where each event is a tuple (t, i, j),
        meaning that an event takes place at time t between nodes i
        and j. Events are undirected. `events` must be sorted by time
        in increasing order.
    events_reversed : iterable (default: None)
        Normally it should be possible to iterate through `events` in
        reversed order. If this is difficult to arrange, you can
        supply `events_reversed` which is then used to go through the
        events in reversed order. In this case `events` can be any
        iterable object.
    nodeBetweenness : dict (default: None)
        If an empty dictionary is given, node event betweenness will
        be calculated and saved in it, with a key corresponding to the
        node id.
    include_path_ends : bool (default: False)
        If True, the ends of the paths are included when calculating
        the node event betweenness. Otherwise only paths that go
        _through_ the node are counted.

    Yield
    -----
    (t, event_betweenness) : (int, int)
        At each iteration an event time is returned with the
        corresponding event betweenness. The values are returned in
        the same order as in `events`.

    Notes
    -----
    Both the time and space complexity of this algorithm are linear.
    """

    # Preprocessing:
    if events_reversed is None:
        events_reversed = reversed(events)

    # Phase I: Build the number of leaving paths.
    L_count = {}
    L_diff = deque()
    for t, i, j in events_reversed:
        l_i = L_count.setdefault(i, 0)
        l_j = L_count.setdefault(j, 0)
        c_new = l_i + l_j + 1
        L_diff.append((c_new-l_i, c_new-l_j))
        L_count[i] = L_count[j] = c_new

    # Phase II: Calculate event betweenness.
    A_count = {}
    for t, i, j in events:
        # Invariants:
        #   A_count[i] contains the number of paths arriving at node i
        #   before the current event.
        #   L_count[i] contains the number of paths leaving from node i
        #   at or after the current event.

        # Get the number of paths arriving to nodes i and j before the
        # current event.
        a_i = A_count.setdefault(i, 0)
        a_j = A_count.setdefault(j, 0)

        # Update L_count to get the number of leaving paths after the
        # current event.
        i_update, j_update = L_diff.pop()
        L_count[i] -= i_update
        L_count[j] -= j_update
        l_i, l_j = L_count[i], L_count[j]

        # FOR DEBUGGING:
        #print ("t = %d, Arr(%d) = %d, Lea(%d) = %d, Arr(%d) = %d, Lea(%d) = %d" 
        #       % (t, i, a_i, i, l_i, j, a_j, j, l_j))

        # Calculate node betweenness if required. Count only paths
        # arriving at node i via the current event; this way each
        # path is only counted once.
        if nodeBetweenness is not None:
            nb_i = nodeBetweenness.setdefault(i,0) + a_j*l_i + l_i
            nb_j = nodeBetweenness.setdefault(j,0) + a_i*l_j + l_j
            if include_path_ends:
                # Add the contribution of paths starting from or
                # ending at the current event. Because no other
                # adjacent event is involved in these paths, there is
                # no risk of counting them twice.
                nb_i += a_j + l_j
                nb_j += a_i + l_i
            nodeBetweenness[i] = nb_i
            nodeBetweenness[j] = nb_j

        # Yield edge betweenness.
        yield t, a_i*l_j + a_j*l_i + a_i + a_j + l_i + l_j

        # Update the number of paths arriving to nodes i and j at or
        # before the current event.
        c_new = a_i + a_j + 1
        A_count[i] = A_count[j] = c_new 

if __name__ == '__main__':
    """Run unit tests if called."""
    from tests.test_dynamics import *
    unittest.main()
