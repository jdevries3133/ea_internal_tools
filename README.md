# EA Internal Web Apps

This repository contains the web applications that are designed for use by my
colleagues at Empowerment Academy. They may provide some useful shortcut or
tie-in to make some aspect of all of our jobs easier. I envision this site as
a subdomain of empacadmusic.org. The main site will be a statically generated
gatsby / react site, but this will be pure django for the ease of full-stack
integrations.

## Non-Functional Partially Containerized Build

This branch does not work. It is mostly containerized, but my custom
`teacherHelper` library is not released or pulished on PyPi, nor does
it have a convenient build process for the cache, so this was pretty
much a dead end, but some more work on the `teacherHelper` library
could see this branch revisited in the future.
