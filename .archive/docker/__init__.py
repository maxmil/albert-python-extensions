"""
Docker wrapper (prototype)
"""

#  Copyright (c) 2022-2023 Manuel Schneider

from albert import *
import pathlib

md_iid = "0.5"
md_version = "1.2"
md_name = "Docker"
md_description = "Control your docker instance"
md_license = "BSD-3"
md_url = "https://github.com/albertlauncher/python/tree/master/docker"
md_maintainers = "@manuelschneid3r"
md_bin_dependencies = "docker"
md_lib_dependencies = "docker"


class Plugin(QueryHandler):

    def id(self):
        return __name__

    def name(self):
        return md_name

    def description(self):
        return md_description

    def defaultTrigger(self):
        return "d "

    def initialize(self):
        self.icon_running = [str(pathlib.Path(__file__).parent / "running.png")]
        self.icon_stopped = [str(pathlib.Path(__file__).parent / "stopped.png")]
        self.client = docker.from_env()
        if not self.client:
            self.client = docker.DockerClient(base_url='unix://var/run/docker.sock')
            if not self.client:
                raise "Failed to initialize client."


    def handleQuery(self, query):
        for container in self.client.containers.list(all=True):

            # Create dynamic actions
            if container.status == 'running':
                actions = [
                    Action("stop", "Stop container", lambda c=container: c.stop()),
                    Action("restart", "Restart container", lambda c=container: c.restart())
                ]
            else:
                actions = [
                    Action("start", "Start container", lambda c=container: c.start())
                ]
            actions.extend([
                Action("logs", "Logs", lambda c=container.id: runTerminal("docker logs -f %s" % c, close_on_exit=False)),
                Action("remove", "Remove (forced, with volumes)", lambda c=container: c.remove(v=True, force=True)),
                Action("copy-id", "Copy id to clipboard", lambda id=container.id: setClipboardText(id))
            ])

            query.add(Item(
                id=container.id,
                text="%s (%s)" % (container.name, ", ".join(container.image.tags)),
                subtext=container.id,
                icon=self.icon_running if container.status == 'running' else self.icon_stopped,
                actions=actions
            ))

        # for image in reversed(self.client.images.list()):
        #     query.add(Item(
        #         id=image.short_id,
        #         text=str(image.tags),
        #         subtext=image.id,
        #         # icon=self.icon_stopped,
        #         actions=[
        #             Action("run", "Run with command: %s" % query.string,
        #                    lambda i=image, s=query.string: client.containers.run(i, s)),
        #             Action("rmi", "Remove image", lambda i=image: i.remove())
        #         ]
        #     ))
