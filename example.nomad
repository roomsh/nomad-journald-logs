job "logs" {
  datacenters = ["dc1"]
  type        = "system"

  group "logs" {
    task "logs" {
      driver = "docker"

      config {
        image        = "roomsh/nomad-journald-logs:latest"

        mounts = [
          {
            type   = "bind",
            source = "/var/log/journal"
            target = "/var/log/journal"
          },
          {
            type   = "bind",
            source = "/opt/nomad/alloc"
            target = "/allocs"
          }
        ]

        logging {
          type = "journald"
          config {
            mode            = "non-blocking"
            max-buffer-size = "16m"
          }
        }
      }

      resources {
        cpu    = 100
        memory = 128
      }

    }
  }
}

