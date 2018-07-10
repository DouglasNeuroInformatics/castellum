# Subject data

The main purpose of castellum is to handle data of test subjects. It is
important to be able to read and write this data in various ways. We are also
legally required to provide some specific forms of access, e.g. exporting or
deleting all data on a single subject.

On the other hand, we are also required to handle this data very carefully.
Among other things, we are required to split the data so that users can only
ever access the parts of the data they really need.

## Implementation

We chose to not store any data in the `Subject` model. Instead, the data is
split into separate parts (`SubjectData`). The granularity is chosen so that
each part is just big enough to perform a task (e.g. `AttributeSet` is
sufficient to decide whether a subject is suitable for a given study).

Each `SubjectData` belongs to a "domain" and has a pseudonym that uniquely
identifies it in this domain. A separate pseudonym service (implemented in the
`pseudonyms` app) keeps track of which pseudonyms belong to the same `Subject`.

The ID and domain are just strings, no database constructs. This means that the
different parts of a Subject and even the pseudonyms could potentially all be
stored in separate databases or even separate services.

## Security Considerations

The described architecture provides a clear structure for developers that
should help avoiding critical data leaks. Even if an attacker is able to dump a
whole table or even a whole database, this structure still limits the impact.
Even if all `SubjectData` is leaked, attackers would have to guess which parts
belong together.

However, it is important to understand that, since the application has full
access to all data, an attacker can also gain full access to all data.
Spreading the system across several databases on different servers or even in
different organizations does not help much if there is still a single point of
entry.

As a mitigation, services could employ some kind of heuristics to block or at
least warn about suspicious activity. However, deciding what is legitimate and
what is not is far from trivial, especially without the full information that
is available in the main application.
