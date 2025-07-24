from math import atan2, degrees
from typing import Literal

from components.ionode import EnergyIONode, ItemIONode
from core.data_registry import data_registry
from core.entity_manager import entity_manager
from core.event_bus import event_bus
from core.input_manager import input_manager
from core.io_registry import io_registry
from game.power_cable import PowerCable
from game.transfer_link import TransferLink
from core.transfer_registry import transfer_registry, cable_registry
from logger import logger


#* === Base Classes === *#
class Tool:
    def __init__(self, name: str) -> None:
        self.name = name

    def on_select(self): pass
    def on_deselect(self): pass

    def on_mouse_down(self, world_pos, screen_pos, button): pass
    def on_mouse_up(self, world_pos, screen_pos, button): pass

class ToolContext:
    def __init__(self) -> None:
        self.selected_link_type: str | None = None
        self.selected_machine_id: str | None = None
        self.preview_rotation: int = 0

#* === Tool classes === *#
class LinkTool(Tool):
    def __init__(self, tool_manager: "_ToolManager") -> None:
        super().__init__("Link")
        self.start_pos = (0, 0)
        self.end_pos = (0, 0)
        self.type: Literal['item', 'energy', 'fluid']
        self.tool_manager = tool_manager
        self.placing = False
    
    def on_mouse_down(self, world_pos, screen_pos, button):
        self.placing = self.start_placing(world_pos, button)
        # print("mbd")
        
    def start_placing(self, world_pos, button) -> bool:
        if button != 1:
            return False
        if not self.tool_manager.context.selected_link_type:
            logger.warning("[LinkTool] No link selected in tool_manager context!")
            return False
        
        selected_link = data_registry.transfer_links[self.tool_manager.context.selected_link_type]
        
        hovering_item = input_manager.hovered_item
        if hovering_item:
            if isinstance(hovering_item, ItemIONode) and hovering_item.kind == selected_link['type'] and hovering_item.direction == "output":
                self.start_pos = hovering_item.abs_pos
                self.type = hovering_item.kind
                return True
            if isinstance(hovering_item, EnergyIONode) and selected_link["type"] == "power":
                self.start_pos = hovering_item.abs_pos
                self.type = 'energy'
                return True

        # connect to existing link
        for link in transfer_registry.get_links(input_manager.mouse_pos_closest_corner):
            if link.link_id != selected_link["id"]:
                print(link.link_id, selected_link["id"])
                return False
            self.start_pos = link.end_pos
            self.type = link.type
            return True
    
        for link in cable_registry.get_cables(input_manager.mouse_pos_closest_corner):
            if link.link_id != selected_link["id"]:
                print(link.link_id, selected_link["id"])
                return False
            self.start_pos = link.end_pos
            self.type = 'energy'
            return True

        # self.start_pos = world_pos
        # node = io_registry.get_node(self.start_pos)
        # if node:
        #     if node.kind != selected_link['type']:
        #         return False
            
        #     self.type = node.kind
        #     return True
        
        # conveyor = transfer_registry.get_links(self.start_pos)
        # if conveyor:
        #     if conveyor[0].link_id != selected_link['id']:
        #         return False
        #     self.type = conveyor[0].type
        #     return True
        
        # todo allow type to be energy if we are hovering over an energy cable end point
        return False
    
    def on_mouse_up(self, world_pos, screen_pos, button):
        if not self.tool_manager.context.selected_link_type:
            return
        if self.placing:
            hovering_item = input_manager.hovered_item
            end_pos = self.start_pos
            if hovering_item:
                if isinstance(hovering_item, ItemIONode) and hovering_item.kind == self.type and hovering_item.direction == "input":
                    end_pos = hovering_item.abs_pos
                if isinstance(hovering_item, EnergyIONode):
                    end_pos = hovering_item.abs_pos
            else:
                end_pos = input_manager.mouse_pos_closest_corner
            
            # snap end pos to cardinal directions from start_pos
            # todo decide if we need/want to do this at all
            # print(degrees(atan2(end_pos[1]-self.start_pos[1], end_pos[0]-self.start_pos[0])))
            
            if end_pos == self.start_pos:
                self.placing = False
                return
            
            if self.type in ['item', 'fluid']:
                entity_manager.add_entity(TransferLink(self.start_pos, end_pos, self.tool_manager.context.selected_link_type))
            else:
                entity_manager.add_entity(PowerCable(self.start_pos, end_pos, self.tool_manager.context.selected_link_type))
        self.placing = False

#* === ToolManager === *#
class _ToolManager:
    def __init__(self) -> None:
        self.current_tool: Tool | None = None
        self.tools: dict[str, Tool] = {
            "link": LinkTool(self)
        }
        self.context = ToolContext()

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def select_tool(self, tool_id: str):
        if self.current_tool:
            self.deselect_tool()

        new_tool = self.tools.get(tool_id)
        if new_tool:
            self.current_tool = new_tool
            self.current_tool.on_select()
            event_bus.connect("mouse_down", self.current_tool.on_mouse_down)
            event_bus.connect("mouse_up", self.current_tool.on_mouse_up)
        else:
            logger.warning(f"Tool {tool_id} not found in tool list.")

    def deselect_tool(self):
        if self.current_tool:
            event_bus.disconnect("mouse_down", self.current_tool.on_mouse_down)
            event_bus.disconnect("mouse_up", self.current_tool.on_mouse_up)
            self.current_tool.on_deselect()
            self.current_tool = None

tool_manager = _ToolManager()
