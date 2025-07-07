TODO
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
    - [ ] row buttons? ("View Recipe", "Pin Item", "Export", "Trash Item", etc.)
  - [ ] recipe browser (JEI-adjacent)
  - [ ] machine UI
- [ ] conveyors:
  - [x] allow conveyors to be chained together

KNOWN BUGS
- [ ] conveyors don't all stop at the same time when one connected conveyor stops
- [ ] figure out a way to remove the item buffering from conveyor IONodes