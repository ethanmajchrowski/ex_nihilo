# TODO
- [ ] re-implement animations for machines
- [ ] start to add some more machines & recipe trees
- [ ] make MachineType asset_info actually useful
- [ ] fix rendering of machine textures
- [x] output node with multiple conveyor connections should round robin by default (connected input nodes can have priorities later)
- [ ] UI systems
  - [x] basics
  - [ ] machine placement
  - [ ] inventory view
    - [x] basics
    - [x] search
    - [ ] filter (A-Z, reverse, quantity, recently changed, etc. probably going to be a pain in the ass but nice to have)
    - [ ] row buttons for each item? ("View Recipe", "Pin Item", "Export", "Trash Item", etc.)
  - [ ] recipe browser (JEI-adjacent)
  - [ ] machine UI
- [ ] conveyors:
  - [x] allow conveyors to be chained together
  - [ ] allow conveyors to be connected to the input nodes of other conveyors (i.e. two conveyors combining into one)
    - [ ] allow conveyors to be placed without an input node
- [ ] machines
  - [ ] add robust system to manually input and output items with machines
  - [ ] multiblock machines? connected machines that give others buffs/functionality?

# KNOWN BUGS
- [ ] conveyors don't all stop at the same time when one connected conveyor stops
- [ ] figure out a way to remove the item buffering from conveyor IONodes
- [ ] fix conveyor cutting to work with camera offset
- [ ] importer only pulls from first index in inventory, should iterate over each item (going to be a pain in the ass)

# GOALS
## Short-term goals
- [ ] **==== Recipe System Tweaks ====** 
  - [ ] Multi-input/output
    - [ ] ex. "inputs": {"water": 100, "ammonia": 50}, "conditions": {"heat": 500, "pressure": 1000}, "outputs": {"nitric_acid": 30}
    - [ ] Support optional requirements: tiered machine, catalyst, environment
  - [ ] Fluids, gases, energy
  - [ ] Byproducts and chance-based outputs
  - [ ] Multi-step intermediate chains
  - [ ] Heat, pressure, catalyst variables
- [ ] **==== Recipe Browser ====** 
    *goals: Let the player explore recipes easily, view input/output chains, and select for machine use.*
  - [ ] Create UIRecipeBrowserPanel like UIInventoryPanel
  - [ ] Add search/filter bar (by input/output item)
  - [ ] For each recipe: Show inputs & outputs with icons and quantities
  - [ ] Show which machines can use the recipe
  - [ ] Hovering an item highlights all recipes that use/produce it
    - [ ] Click to pin or queue recipe (later use for autoplanners?)
  - [ ] Show required power, duration, and tiers visually
    - [ ] Optionally preview full chains of dependencies
- [ ] **==== World Placement and Crafting ====**
    *Goals: Let the player craft and place machines in the world from inventory.*
  - [x] Show item count and cost in the crafting panel sidebar
  - [x] Add “Craft” button (already done)
  - [ ] Show preview sprite
  - [x] Allow rotating before placing
    - [ ] Validate placement (no overlap, valid terrain)
  - [x] On place: 
    - [x] Remove from global inventory
    - [x] Add to world objects and assign IONodes
- [ ] **Energy System Prototype**
    *Goals: Basic power production and consumption system, visible and functional.*
  - [ ] Define NodeType.ENERGY and support in IONodes
  - [ ] Add energy field to machines (current, required, max)
  - [ ] Create BurnerGenerator:
    - [ ] Accepts fuel items
    - [ ] Outputs energy to output energy nodes
    - [ ] Consumes fuel over time
  - [ ] Create a powered version of a basic machine (e.g., Electric Crusher)
    - [ ] Won’t run without energy flow
  - [ ] Display energy status visually:
    - [ ] Energy bar or icon above machine
  - [ ] Tooltip shows required vs current energy
  - [ ] Update Machine update() to check energy before progressing recipe
- [ ] **Notifications and Visual Indicators**
    *Goals: Make machine state legible: stuck, waiting, missing input, or unpowered.*
  - [ ] Create a lightweight MachineStatus enum (OK, No Input, Output Full, No Power)
  - [ ] Display status icons or color tints near machine
  - [ ] Show tooltip or hover UI explaining current state
  - [ ] Update node/conveyor visuals to show jams (e.g., red outline)
    - [ ] Optional: Log status changes for debugging
## Mid-term goals
- [ ] *Modular Infrastructure Systems*
  - [ ] Add pumps, pipes, and liquid tanks (for fluids like water, oil, lava).
  - [ ] Let recipes require both items and fluids.
  - [ ] Start using water for more advanced ore washing, etc.
- [ ] *Production Statistics / Planning View*
  - [ ] Show item throughput per minute.
  - [ ] View a summary of global item production/consumption.
  - [ ] Useful for optimizing large-scale setups.
- [ ] *Machine Variants*
  - [ ] Machines with more than one tile (e.g. 2x1, 2x2).
  - [ ] Machines with specialized layouts (e.g. input only from back, output only from front).
  - [ ] Add support for visual multi-tile machines (not just logic).
- [ ] *Passive Item Generators*
  - [ ] Add mineshafts or extractors that produce items or fluids over time.
  - [ ] May require nearby support buildings or powered enhancements.
  
## Long-Term (High-value features, polish, and stretch goals)
- [ ] *Multiblock Machines*
  - [ ] Structures composed of multiple placed parts that form one machine.
  - [ ] For example: a 3x3 boiler, a 2x2 chemical reactor.
- [ ] *Transport Alternatives*
  - [ ] Add underground belts, pipes, drone delivery, or minecarts.
  - [ ] Tradeoffs between complexity, throughput, space.
- [ ] *Power Grids / Wiring*
  - [ ] Power lines, substations, etc.
  - [ ] Add different energy types: steam, solar, nuclear.
  - [ ] Power loss over distance or capacity caps.
- [ ] *Building Tiers / Infrastructure Progression*
  - [ ] Machines require more infrastructure (e.g., concrete floor for heavy machines).
  - [ ] Reinforce the infrastructure-as-progression design.



🔁 5. Crafting Queue & Automation Planning (optional)

Start thinking about how crafting can scale and be automatable later.
Tasks:
Add CraftingQueue system (or planned actions list)
Show items queued for crafting, in-progress, and completed
    (Later) Allow machines to craft things when materials available
Bonus UI polish:
    Add subtle animations for crafting / placement / recipe selection
    Use item images in tooltips and recipe previews
    Right-click on items in any UI panel brings up context menu (e.g., "View Recipes", "Pin", "Track")