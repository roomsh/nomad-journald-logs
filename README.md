# nomad-journald-logs
A simple tool to stream logs from journald into log files for nomad. This allows display of the logs in the nomad ui, without the overhead of running nomad's docker collecting daemon.

## Getting started
An example Nomad job file is available at `example.nomad`. `nomad-journald-logs` is designed to be easily run as a system job on the cluster, and needs access to `/var/log/journal`, `/etc/machine-id` and the Nomad allocation directory. You'll need to make sure that Nomad's Docker driver is set to allow arbitary volume mounts.
