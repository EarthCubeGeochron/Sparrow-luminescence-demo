# Sparrow luminescence example

This is a test laboratory implementation of [**Sparrow**](https://sparrow-data.org)
for optically-stimulated luminescence (OSL) data.

## Installation

Installation presumes Linux or MacOS (Windows support is in progress).
To install Sparrow and load test DRILL data, take the following steps
(abbreviated and updated from Sparrow's [documentation](https://sparrow-data.org/installation/)).

1. Install required dependencies (basically `Docker` and `zsh`). Make sure Docker is running.
2. Clone this repository, and install submodules with `git submodule update --init --recursive`.
   This will install the proper version of Sparrow and its submodule components.
3. Create a `sparrow-secrets.sh` file in this directory (using the supplied template),
   with the appropriate values for secrets.
4. Optionally, create a `sparrow-config.overrides.sh` file in this directory (using the supplied template),
   if you want to override variables such as `SPARROW_ENV` without committing the changes.
5. Make sure that `Sparrow/bin/sparrow` (the main Sparrow executable) is linked
   to your path, or otherwise runnable.
6. Run `sparrow up` to install Sparrow and create the database. Sparrow will be running
   at `http://localhost:5002`, unless you changed the `SPARROW_HTTP_PORT` configuration variable.

Once you have a running instance of Sparrow, you can run a few operations to load data:

- `sparrow import-osl`: import DRILL test data.
- `sparrow create-user`: create an authorized user.
- `sparrow update-location-names`: get named locations for imported samples.

## Usage

The `Sparrow/bin/sparrow` command should be linked or aliased to your `$PATH`
in order to drag in the executables in this repository. `sparrow` and
its subcommands should be run from this directory or a subdirectory.

## About the test dataset (compiled by Christina Neudorf)

I’ve compiled age data for 13 projects that the DRI Lum Lab (DRILL) has
generated ages for (attached). Each project has two tabs: the first include the
age data, and the second, labelled “PROJECT ID test dose signal” includes an
example of a luminescence signal from a sample of that project (typically
plotted as “stimulation time vs photon cts”). The luminescence community has
brainstormed ways to organize data in an online database for Luminescence data,
so the age data tab is formatted according to suggestions from the Lum
community. There are a few blank cells where the column is not applicable, or
data for that sample is missing.  Are you able to use this to provide us with a
“demo” of Sparrow in action? The entry formats in the second row of the age data
tabs can probably be deleted for your purposes.

Of course each luminescence age is also associated with one or more Sequence
Editor (.SEQ) and Bin (.bin or .binx) files. The former is instructions to our
machine on how to measure the sample, and the latter is the measured data itself
(typical examples attached). We’ve considered making these available to database
users by linking them to each age, so if you think you are able to incorporate
them into Sparrow somehow, let me know, and I’ll send them to you. If Sparrow
can link these raw datafiles to each age, then the test dose signal data I’ve
included in the spreadsheet would no longer be necessary.
