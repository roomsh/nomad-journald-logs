#!/usr/bin/env python3
import re
import select

from pathlib import Path

from systemd import journal

alloc_re = re.compile(r"(.*)\-(\b[0-9a-f]{8}\-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b)")
alloc_base = Path('/allocs')

j = journal.Reader(flags=journal.SYSTEM_ONLY)
j.log_level(journal.LOG_INFO)

j.add_match(_SYSTEMD_UNIT="docker.service")
j.seek_tail()
j.get_previous()

p = select.poll()
p.register(j, j.get_events())

handlers = {}

class NomadLogHandler:
    def __init__(self, log_dir, log_name, max_bytes, backup_count):
        self.log_dir = log_dir
        self.log_name = log_name
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        self.current_index = self._get_current_index()
        self._open_stream()

    def _get_current_index(self):
        existing_log_files = [str(x).rpartition('.') for x in self.log_dir.glob(f'{self.log_name}.*')]
        current_index = 0
        for _, _, idx in existing_log_files:
            try:
                current_index = max(current_index, int(idx))
            except:
                print(f"nomad-journald-logs: Invalid log file idx: {idx}")
                continue

        return current_index

    def _open_stream(self):
        self.stream = open(str(self.log_dir / self.log_name) + f'.{self.current_index}', 'a')

    def log(self, msg):
        self.stream.write(msg + '\n')
        self.stream.flush()
        try:
            self.check_rollover()
        except:
            print(f"nomad-journald-logs: error trying to check for rollover")

    def check_rollover(self):
        # max_bytes is more like a guideline.
        if self.stream.tell() >= self.max_bytes:
            self.stream.close()
            self.current_index += 1
            self._open_stream()

        # Prune any previous logs more than backup_count ago.
        threshold = self.current_index - self.backup_count
        existing_log_files = [(x, str(x).rpartition('.')[2]) for x in self.log_dir.glob(f'{self.log_name}.*')]
        for path, idx in existing_log_files:
            try:
                idx = int(idx)
            except:
                print(f"nomad-journald-logs: Invalid log file idx: {idx}")
                continue

            if idx < threshold:
                try:
                    print(f"nomad-journald-logs: unlinking log file {path}")
                    path.unlink()
                except:
                    print(f"nomad-journald-logs: error unlocking log file {path}")

print("nomad-journald-logs: polling for journald logs")
while p.poll():
    if j.process() != journal.APPEND:
        continue

    for entry in j:
        if not 'CONTAINER_NAME' in entry:
            continue

        container_name = entry['CONTAINER_NAME']

        match = alloc_re.match(container_name)
        if not match:
            continue

        task_name = match.group(1)
        alloc_id = match.group(2)

        if container_name not in handlers:
            log_dir = alloc_base / alloc_id / "alloc" / "logs"

            # Skip entries where we don't have a log_dir.
            if not log_dir.exists():
                continue

            log_name = f"{task_name}.stdout"

            # Match nomad's defaults of 10MB / 10 files
            handlers[container_name] = NomadLogHandler(log_dir, log_name, max_bytes=10*1024*1024, backup_count=10)
            print(f"nomad-journald-logs: found new container_name: {container_name}. will write logs to: {log_dir / log_name}")

        log_line = str(entry['__REALTIME_TIMESTAMP']) + ' ' + entry['MESSAGE']
        handlers[container_name].log(log_line)
