# Subject data

The main purpose of castellum is to handle data of test subjects. It is
important to be able to read and write this data in various ways. We are
also legally required to provide some specific forms of access, e.g.
exporting or deleting all data on a single subject.

On the other hand, we are also required to handle this data very
carefully. Among other things, we are required to split the data so that
users can only ever access the parts of the data they really need.

## Implementation

We chose to split the data into three different categories:

-   Scientific data is handled outside of castellum. Castellum only
    provides the pseudonyms that are used to map this data to subjects.
-   Data relevant for recruitment is handled in castellum.
-   Contact data is also handled in castellum, but in a separate
    database to provide an additional barrier.

## Security Considerations

The described architecture provides a clear structure for developers
that should help avoiding critical data leaks. Even if an attacker is
able to dump a whole table or even a whole database, this structure
still limits the impact.

However, it is important to understand that the barrier between
recruitment and contact data is not that high. Since castellum has full
access to both, an attacker can also gain full access. Spreading the
system across several databases on different servers or even in
different organizations does not help much if there is still a single
point of entry.
