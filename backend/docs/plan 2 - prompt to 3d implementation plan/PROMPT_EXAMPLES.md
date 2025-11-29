# CADLift Prompt-to-3D Examples

This document provides comprehensive examples of prompts you can use with the CADLift prompt-to-3D feature. All examples generate realistic, production-quality 3D models.

---

## Table of Contents

1. [Simple Objects](#simple-objects)
2. [Containers & Vessels](#containers--vessels)
3. [Mechanical Parts](#mechanical-parts)
4. [Decorative Items](#decorative-items)
5. [Buildings & Rooms](#buildings--rooms)
6. [Advanced Examples](#advanced-examples)
7. [Tips for Best Results](#tips-for-best-results)

---

## Simple Objects

### Basic Cylinder
```
"A simple cylinder, 100mm tall, 50mm diameter"
```
**Generated**: Straight cylinder, 100mm × 50mmø

### Basic Box
```
"A box, 80mm wide, 60mm long, 40mm tall"
```
**Generated**: Rectangular box with specified dimensions

### Hollow Cylinder
```
"A hollow cylinder, 100mm tall, 50mm diameter, 3mm wall thickness"
```
**Generated**: Hollow tube with 3mm walls

---

## Containers & Vessels

### Coffee Cup (Simple)
```
"A realistic coffee cup, 90mm tall"
```
**Generated**: Tapered cylinder, hollow, ~70-90mm diameter, 3mm walls

### Coffee Cup (Detailed)
```
"Create a realistic coffee cup with a handle. The cup should be 90mm tall
with a 75mm outer diameter at the top, tapering to 60mm at the base.
Wall thickness of 3mm. Add a curved handle attached to the side, 40mm
wide and 70mm tall. Apply 2mm fillet to all edges for a smooth finish."
```
**Generated**: Tapered body + sweep handle + filleted edges

### Coffee Mug
```
"A coffee mug, 100mm tall, 85mm diameter, with a handle"
```
**Generated**: Tapered cylinder + curved handle

### Water Bottle
```
"Create a water bottle, 200mm tall, narrow at bottom, wider at top"
```
**Generated**: Tapered bottle body + cap/neck

### Water Bottle (Detailed)
```
"Water bottle, 200mm tall, 65mm diameter, with threaded neck for cap"
```
**Generated**: Tapered body + threaded neck (M28 thread)

### Glass Tumbler
```
"A glass tumbler, 120mm tall, 70mm diameter at top, 60mm at bottom"
```
**Generated**: Tapered glass with realistic proportions

### Jar
```
"A jar for storage, 150mm tall, 80mm wide, hollow"
```
**Generated**: Cylindrical jar with walls

---

## Mechanical Parts

### Screw (Simple)
```
"A screw, 30mm long"
```
**Generated**: Thread + head + tip

### Screw (Detailed)
```
"M6 screw, 30mm long with Phillips head"
```
**Generated**: M6 thread (pitch 1mm) + head + tip

### Bolt
```
"An M8 bolt, 40mm long"
```
**Generated**: M8 thread + hexagonal head

### Nut
```
"An M6 nut, hexagonal"
```
**Generated**: Hexagonal polygon with threaded center

### Washer
```
"A washer, 20mm outer diameter, 10mm inner diameter, 2mm thick"
```
**Generated**: Flat ring with specified dimensions

### Power Adapter
```
"A power adapter with rectangular body and plug"
```
**Generated**: Box body + smaller box plug + filleted edges

---

## Decorative Items

### Vase (Simple)
```
"A vase, 250mm tall"
```
**Generated**: Tapered vase, wider at top

### Vase (Detailed)
```
"A decorative vase, narrow bottom (60mm), wide top (100mm), 300mm tall"
```
**Generated**: Smooth tapered vase with artistic proportions

### Flower Pot
```
"A flower pot, 150mm tall, 120mm diameter at top, 80mm at bottom"
```
**Generated**: Tapered pot with drainage consideration

### Candle Holder
```
"A candle holder, cylindrical, 80mm tall, 60mm diameter, hollow center"
```
**Generated**: Hollow cylinder for candle

### Bowl
```
"A bowl, wide opening, 150mm diameter, 60mm deep"
```
**Generated**: Shallow cylindrical bowl

---

## Buildings & Rooms

### Simple Room
```
"A 6x4 meter room"
```
**Generated**: Rectangular room, 6000mm × 4000mm, 3000mm tall

### Room (Detailed)
```
"A 5x4 meter bedroom, 2.8 meters tall, 200mm wall thickness"
```
**Generated**: Room with specified dimensions and walls

### Multi-Room Layout
```
"A 2 bedroom apartment, 10x8 meters total"
```
**Generated**: Multiple rooms arranged side-by-side

### Office
```
"An office space, 8x6 meters, with closet"
```
**Generated**: Main office + smaller closet room

---

## Advanced Examples

### Funnel
```
"A funnel for liquids, wide top (120mm), narrow bottom (20mm), 150mm tall"
```
**Generated**: Inverted tapered cylinder (funnel shape)

### Pipe Connector
```
"A pipe connector, 50mm diameter, with threaded ends"
```
**Generated**: Cylinder with threads on both ends

### Pencil Holder
```
"A pencil holder, cylindrical, 100mm tall, 80mm diameter, hollow"
```
**Generated**: Hollow cylinder suitable for pencils

### Bottle Cap
```
"A bottle cap, 40mm diameter, 15mm tall, with internal threads"
```
**Generated**: Hollow cylinder with internal threading

### Thread Adapter
```
"A thread adapter, M6 on one end, M8 on other end, 30mm long"
```
**Generated**: Two different threads connected

### Multi-Part Assembly
```
"A container with a lid: main body 100mm tall, 80mm diameter, lid 20mm tall"
```
**Generated**: Separate body and lid parts

---

## Tips for Best Results

### Specify Dimensions
✅ **Good**: "Coffee cup, 90mm tall, 75mm diameter"
❌ **Avoid**: "A cup" (dimensions may vary)

### Use Realistic Sizes
- Coffee cups: 80-120mm tall, 70-90mm diameter
- Water bottles: 180-250mm tall, 60-80mm diameter
- Screws: 10-50mm long, 3-10mm diameter
- Rooms: 3000-5000mm tall, 2000-10000mm wide

### Describe Tapering
✅ **Good**: "narrow at bottom, wide at top"
✅ **Good**: "tapering from 60mm to 75mm"
❌ **Avoid**: Just "cone" (less precise)

### Specify Wall Thickness
✅ **Good**: "hollow with 3mm walls"
✅ **Good**: "2mm wall thickness"

### Request Features
- **Hollow**: "hollow", "empty inside", "with walls"
- **Filleted**: "rounded edges", "smooth corners", "2mm fillet"
- **Threaded**: "with threads", "M6 thread", "threaded neck"
- **Handle**: "with handle", "with curved handle"

### Combine Features
```
"A coffee mug, 100mm tall, tapered from 70mm to 85mm diameter,
hollow with 3mm walls, with a curved handle, and 2mm rounded edges"
```

---

## Object vs Building Detection

The system automatically detects whether you want an object or a building:

### Objects (use shapes)
Keywords: mug, cup, bottle, vase, screw, adapter, tool, part, component

### Buildings (use rooms)
Keywords: room, house, apartment, office, kitchen, bedroom, floor plan

**If unclear**, be specific:
- ✅ "Create a 3D model of a coffee cup" (object)
- ✅ "Design a 6x4 meter room layout" (building)

---

## Common Patterns

### Pattern 1: Simple Container
```
"[Object type], [height], [diameter], hollow"
```
Example: "A jar, 150mm tall, 80mm diameter, hollow"

### Pattern 2: Tapered Container
```
"[Object type], [height], [bottom size] at bottom, [top size] at top"
```
Example: "A vase, 250mm tall, 60mm at bottom, 100mm at top"

### Pattern 3: With Handle
```
"[Object type], [height], with a curved handle"
```
Example: "A mug, 100mm tall, with a curved handle"

### Pattern 4: Threaded Part
```
"[Thread size] [part type], [length]"
```
Example: "M6 screw, 30mm long"

### Pattern 5: Multi-Part
```
"[Object type] with [additional part]: [main specs], [part specs]"
```
Example: "A bottle with cap: 200mm tall, cap 20mm"

---

## Output Quality Metrics

After generation, check the quality metrics in the job output:

```json
{
  "quality_metrics": {
    "detail_level": 70,
    "model_source": "shapes",
    "shapes_generated": 2,
    "advanced_features_used": {
      "tapered": true,
      "threaded": false,
      "hollow": true,
      "filleted": true,
      "sweep": true,
      "revolve": false
    },
    "advanced_feature_count": 3,
    "shape_types": {
      "tapered_cylinder": 1,
      "sweep": 1
    },
    "polygon_count": 2,
    "total_vertices": 128
  }
}
```

**Metrics Explained**:
- `detail_level`: Smoothness (10-100, higher = smoother curves)
- `shapes_generated`: Number of parts created
- `advanced_features_used`: Which advanced features were used
- `shape_types`: Distribution of shape types
- `polygon_count`: Complexity indicator
- `total_vertices`: Total vertices in model

---

## Troubleshooting

### Problem: Object too simple
**Solution**: Add more details in prompt
```
Before: "A cup"
After: "A coffee cup, 90mm tall, tapered, hollow with 3mm walls, with handle"
```

### Problem: Wrong type (building instead of object)
**Solution**: Use object keywords explicitly
```
Before: "A room for bottles"
After: "A bottle, 200mm tall"
```

### Problem: Dimensions unrealistic
**Solution**: Specify realistic sizes
```
Before: "A tiny cup" (ambiguous)
After: "A cup, 90mm tall" (specific)
```

### Problem: Missing features
**Solution**: Request explicitly
```
Before: "A mug"
After: "A mug, hollow with 3mm walls, with handle, rounded edges"
```

---

## Export Formats

Generated models are available in:
- **DXF**: 2D footprint + 3D mesh (universal CAD format)
- **STEP**: 3D solid model (industry standard)
- **Metadata JSON**: Instructions and quality metrics

---

## Version History

### Phase 2 (Current)
- ✅ Tapered cylinder support
- ✅ Realistic dimension guidelines
- ✅ Coffee cup with handle examples
- ✅ Quality metrics tracking

### Phase 1
- ✅ Thread, revolve, sweep shapes
- ✅ Better error logging
- ✅ Object detection

---

**Need Help?** Check the logs for warnings if features fail, or simplify your prompt and add complexity gradually.

**Happy Modeling!** 🎨✨
