#
# python-bluetooth-mesh - Bluetooth Mesh for Python
#
# Copyright (C) 2019  SILVAIR sp. z o.o.
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#
# pylint: disable=C0415,E0401

"""
Application mixins.
"""
from typing import List, Mapping, Optional, Tuple, Union
from uuid import uuid5

from aiohttp import ClientSession
from platforms_clients.commissioning.client import (
    AsyncCommissioningClient,
    PlatformEnvironment,
)
from platforms_clients.commissioning.representation import entities, schemas
from prompt_toolkit import PromptSession

from bluetooth_mesh.application import (
    ApplicationKeyMixin,
    MachineUUIDMixin,
    NetworkKeyMixin,
)
from bluetooth_mesh.crypto import ApplicationKey, DeviceKey, NetworkKey
from bluetooth_mesh.interfaces import ManagementInterface


class NetworkAwarenessMixin:
    """
    An extension to application that's able to use a Network entity instance exported from Commissioning.
    It requires the following fields:
        * `network` - a `Network` loaded from Commissioning
        * `primary_net_key_index` - index of the network key to use
        * `management_interface` - interface to `meshd`, capable of importing remote nodes
    """

    network = None  # type: Optional[entities.Network]
    primary_net_key_index = 0  # type: int
    management_interface = None  # type: ManagementInterface

    @property
    def primary_net_key(self) -> Tuple[int, NetworkKey]:
        net_key = next(
            net_key
            for net_key in self.network.network_keys
            if net_key.index == self.primary_net_key_index
        )

        return net_key.index, NetworkKey(net_key.bytes)

    @property
    def subnets_net_keys(self) -> List[Tuple[int, NetworkKey]]:
        net_keys = []

        for net_key in self.network.network_keys:
            if net_key.index == self.primary_net_key_index:
                continue

            net_keys.append((net_key.index, NetworkKey(net_key.bytes)))

        return net_keys

    @property
    def app_keys(self) -> List[Tuple[int, int, ApplicationKey]]:
        app_keys = []

        for app_key in self.network.application_keys:
            app_keys.append(
                (app_key.index, app_key.bound, ApplicationKey(app_key.bytes))
            )

        return app_keys

    async def import_nodes(self):
        """Imports all nodes from used network into `meshd`, enabling communication with them using device keys."""
        for node in self.network.nodes:
            # don't overwrite my own key
            if node.address == self.addr:
                continue

            await self.management_interface.import_remote_node(
                node.address, len(node.elements), DeviceKey(node.device_key.bytes)
            )


class Network(entities.Network):
    areas = {}  # type: Mapping[str, Area]


class NetworkSchema(schemas.NetworkSchema):
    entity_class = Network


class Area(entities.Area):
    zones = {}  # type: Mapping[str, entities.Zone]


class AreaSchema(schemas.AreaSchema):
    entity_class = Area


class PlatformLoginMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = None

    async def get_login(self):
        raise NotImplementedError

    async def get_password(self):
        raise NotImplementedError

    async def get_project(self, projects):
        raise NotImplementedError

    def get_namespace(self):
        namespace = super().get_namespace()
        return uuid5(namespace=namespace, name=self.project.project_id)

    async def platform_login(self, get_address=True) -> Tuple[Optional[int], Network]:
        login = await self.get_login()
        password = await self.get_password()

        async with ClientSession() as session:
            client = AsyncCommissioningClient(
                login,
                password,
                session=session,
                environment=PlatformEnvironment.PREPROD,
            )

            self.logger.info("Logging in: %s", login)

            projects = await client.get_projects()
            self.project = await self.get_project(projects)
            assert self.project is not None

            self.logger.info("Selected project: %s", self.project.name)

            network = await client.get_network(
                self.project.project_id, schema=NetworkSchema
            )
            if get_address:
                (address,) = await client.get_app_addresses(
                    application_uuid=str(self.uuid),
                    project_id=self.project.project_id,
                    amount=1,
                )

                self.logger.info(
                    "Obtained address for application %s: %04x", self.uuid.hex, address
                )
            else:
                address = None

            for area in await client.get_areas(
                self.project.project_id, schema=AreaSchema
            ):
                for zone in await client.get_zones(
                    self.project.project_id, area.area_id
                ):
                    area.zones[zone.zone_id] = zone

                network.areas[area.area_id] = area

            return address, network


class CommandLineMixin:
    def __init__(self, loop, arguments):
        super().__init__(loop)
        self.arguments = arguments

    async def get_login(self):
        login = self.arguments.get("--login")

        if login is None:
            login = await PromptSession().prompt(
                message="login: ", is_password=False, async_=True
            )
        return login

    async def get_password(self):
        password = self.arguments.get("--password")

        if password is None:
            password = await PromptSession().prompt(
                message="password: ", is_password=True, async_=True
            )

        return password

    async def get_project(self, projects):
        project_name = self.arguments.get("--project")

        if project_name is None:
            for index, project in enumerate(projects):
                print("%-4d: %s (%s)" % (index, project.name, project.project_id))

            index = await PromptSession().prompt(
                message="project: ", is_password=False, async_=True
            )

            return projects[int(index)]

        return next((p for p in projects if p.name == project_name), None)

    @staticmethod
    async def _get_project(login_session, project, projects):
        index = 0
        if not project or project not in [_project.name for _project in projects]:
            for _project in projects:
                print("  %s: %s" % (index, _project.name))
                index += 1

            selection = await login_session.prompt(
                message="Select project: ", is_password=False, async_=True
            )
        else:
            selection = [_project.name for _project in projects].index(project)

        return projects[int(selection)]
