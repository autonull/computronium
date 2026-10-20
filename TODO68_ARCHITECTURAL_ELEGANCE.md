# TODO68 Architectural Elegance Review

**Purpose**: Identify Single-Source-of-Truth, DRY, and metaprogramming opportunities for the dashboard implementation.

---

## 1. WebSocket Message Handler Registry (Eliminate Manual Routing)

### Current Plan (Manual)
```typescript
// src/ws-client.ts - MANUAL ROUTING
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  switch (msg.type) {
    case 'status_update': handleStatus(msg.data); break;
    case 'queue_update': handleQueue(msg.data); break;
    case 'campaign_metrics': handleMetrics(msg.campaign_id, msg.data); break;
    case 'pipeline_event': handlePipeline(msg); break;
    default: console.warn('Unknown message type', msg.type);
  }
};
```

### Elegant Alternative: Registry Pattern
```typescript
// src/ws-client.ts - REGISTRY-BASED
type Handler<T> = (data: T) => void;

class MessageRouter {
  private handlers = new Map<string, Handler<any>[]>();

  register<T>(type: string, handler: Handler<T>) {
    this.handlers.set(type, [...(this.handlers.get(type) || []), handler]);
  }

  route(msg: WSMessage) {
    const handlers = this.handlers.get(msg.type);
    if (!handlers) {
      console.warn(`No handler for ${msg.type}`);
      return;
    }
    handlers.forEach(h => h(msg));
  }
}

// Components self-register
const router = new MessageRouter();

// In DiscoveryMap constructor:
router.register('queue_update', this.onQueueUpdate.bind(this));
router.register('campaign_metrics', this.onMetrics.bind(this));

// In LiveRail constructor:
router.register('pipeline_event', this.onPipelineEvent.bind(this));

// In HUD constructor:
router.register('status_update', this.onStatus.bind(this));
```

**Benefits**:
- Zero boilerplate in `ws-client.ts`
- Components declare their own subscriptions (explicit dependencies)
- Easy to add new message types without touching router
- Testable: mock router, verify registrations

---

## 2. Dashboard Component Registry (Auto-Discovery)

### Current Plan (Manual Imports)
```typescript
// src/main.ts - MANUAL
import { DiscoveryMap } from './discovery-map.js';
import { CellDrawer } from './cell-drawer.js';
import { Plotter } from './plotter.js';
import { LiveRail } from './live-rail.js';
import { HUD } from './hud.js';

const discoveryMap = new DiscoveryMap(scene);
const cellDrawer = new CellDrawer();
const plotter = new Plotter();
const liveRail = new LiveRail();
const hud = new HUD(scene);
```

### Elegant Alternative: Plugin Registry
```typescript
// src/components/registry.ts
interface DashboardComponent {
  name: string;
  init(ctx: ComponentContext): void | Promise<void>;
  destroy(): void;
}

const componentRegistry = new Map<string, DashboardComponent>();

export function registerComponent(comp: DashboardComponent) {
  componentRegistry.set(comp.name, comp);
}

// In each component file:
export const DiscoveryMap: DashboardComponent = {
  name: 'discovery-map',
  init(ctx) { /* ... */ },
  destroy() { /* ... */ }
};
registerComponent(DiscoveryMap);

// src/main.ts - AUTO-DISCOVERY
async function initComponents(ctx: ComponentContext) {
  for (const [name, comp] of componentRegistry) {
    await comp.init(ctx);
    console.log(`Initialized ${name}`);
  }
}
```

**Benefits**:
- Add new component = create file + export, no `main.ts` edit
- Explicit lifecycle (`init`/`destroy`) for cleanup
- Dependency injection via `ComponentContext` (scene, router, store)
- Hot-reload friendly in dev

---

## 3. Chart Type Registry (Plotter Extensibility)

### Current Plan (Hardcoded Tabs)
```typescript
// src/plotter.ts - HARDCODED
class Plotter {
  private charts = {
    pareto: new ParetoChart(),
    ablation: new AblationChart(),
    variability: new VariabilityChart(),
  };
  // ...
}
```

### Elegant Alternative: Chart Registry
```typescript
// src/plotter/chart-registry.ts
interface ChartSpec {
  id: string;
  label: string;
  create(): Chart;
  dataRequirements: string[]; // e.g. ['val_acc', 'walltime_s', 'param_count']
}

const chartRegistry = new Map<string, ChartSpec>();

export function registerChart(spec: ChartSpec) {
  chartRegistry.set(spec.id, spec);
}

// In ParetoChart.ts:
registerChart({
  id: 'pareto',
  label: 'Pareto Frontier',
  create: () => new ParetoChart(),
  dataRequirements: ['val_acc', 'walltime_s', 'param_count']
});

// In Plotter.ts:
class Plotter {
  private activeChart: Chart | null = null;

  setChart(id: string, data: Record[]) {
    const spec = chartRegistry.get(id);
    if (!spec) throw new Error(`Unknown chart: ${id}`);
    
    // Validate data has required fields
    const missing = spec.dataRequirements.filter(
      req => !data.some(d => req in d.payload)
    );
    if (missing.length) throw new Error(`Missing data: ${missing.join(', ')}`);
    
    this.activeChart?.destroy();
    this.activeChart = spec.create();
    this.activeChart.update(data);
  }
}
```

**Benefits**:
- New chart = 1 file + register, no Plotter edit
- Data requirements declared → automatic validation
- Could load charts dynamically (code splitting)

---

## 4. Axis Metadata Registry (Discovery Map Flexibility)

### Current Plan (Hardcoded Axis Config)
```typescript
// src/discovery-map.ts - HARDCODED
private axes: AxesConfig = { x: 'credit', y: 'geometry', z: 'dynamics' };
```

### Elegant Alternative: Axis Registry (Leverage Existing!)
```typescript
// The codebase ALREADY HAS: StructuralAxis enum + AXES_REGISTRIES
// src/discovery-map.ts - DATA-DRIVEN

import { StructuralAxis, get_registry } from 'computronium/experiment/schema/axis';

// But we need this in TypeScript... Solution: GENERATE from Python
// scripts/generate_axis_metadata.py → src/axis-metadata.json

interface AxisMeta {
  key: string;
  label: string;
  color: number;
  extractor: (record: Record) => string; // runtime function
}

const AXIS_METADATA: AxisMeta[] = [
  { key: 'credit', label: 'Credit Assignment', color: 0x58a6ff, extractor: r => r.credit },
  { key: 'geometry', label: 'Geometry', color: 0x3fb950, extractor: r => r.geometry },
  // ... from generated JSON
];

class DiscoveryMap {
  // Axes derived from actual data + metadata
  getAxes(records: Record[]): AxisConfig {
    const available = AXIS_METADATA.filter(meta => 
      new Set(records.map(meta.extractor)).size > 1
    );
    return { x: available[0].key, y: available[1].key, z: available[2].key };
  }
}
```

**Python Generator** (`scripts/generate_axis_metadata.py`):
```python
from computronium.experiment.schema.axis import StructuralAxis, get_registry

def generate():
    axes = []
    for axis in StructuralAxis:
        registry = get_registry(axis)
        primitives = list(registry.keys())
        axes.append({
            'key': axis.value,
            'label': axis.value.replace('_', ' ').title(),
            'primitives': primitives,
            'color': PALETTE.arms.get(primitives[0], 0x888888),  # first primitive color
        })
    write_json('src/axis-metadata.json', axes)
```

**Benefits**:
- Single source: Python axis registries
- New primitive registered in Python → auto-appears in dashboard
- No hardcoded axis lists in TypeScript

---

## 5. Color Palette: Single Source with Codegen

### Current Plan (Duplicated)
```python
# computronium/visualization/_style.py (Python)
COLOR_ARM = "#2f6f4f"
# ...

# src/style.ts (TypeScript) - MANUAL COPY
export const PALETTE = { arms: { gradient: 0x58a6ff, ... } };
```

### Elegant Alternative: Generate Both from Single Source
```python
# scripts/generate_palette.py
PALETTE_SOURCE = {
    'bg': '#0a0e14',
    'grid': '#1f2a3a',
    'measured': '#d4a843',
    'legal': '#30363d',
    'void': '#f85149',
    'arms': {
        'gradient': '#58a6ff',
        'pepita': '#d4a843',
        'random_projections': '#3fb950',
        'local_goodness': '#a371f7',
    },
    'chance': '#888888',
    'insufficient': '#d4a843',
    'passed': '#3fb950',
    'rejected': '#f85149',
    'gpu': '#58a6ff',
    'cpu': '#3fb950',
    'memory': '#d4a843',
}

def generate():
    # Python version (for matplotlib backend charts)
    write_python('computronium/visualization/_palette.py', PALETTE_SOURCE)
    
    # TypeScript version (for three.js)
    ts = convert_to_ts(PALETTE_SOURCE)  # hex → 0xRRGGBB
    write_ts('src/palette.ts', ts)
    
    # CSS version (for HTML overlays)
    css = convert_to_css_vars(PALETTE_SOURCE)
    write_css('templates/static/css/palette.css', css)
```

**Benefits**:
- One source of truth for all colors
- Python backend charts (if any) match frontend exactly
- CSS variables for HTML overlays auto-synced

---

## 6. WebSocket Message Types: Python → TypeScript Codegen

### Current Plan (Manual Sync)
```python
# web.py (Python) - message types defined inline
await ws.send_json({"type": "campaign_metrics", "campaign_id": ..., "data": ...})
```

```typescript
// src/ws-client.ts (TypeScript) - MANUAL COPY
type WSMessage = 
  | { type: 'status_update'; data: StatusData }
  | { type: 'campaign_metrics'; campaign_id: string; data: CampaignMetrics }
  // ...
```

### Elegant Alternative: Single Source with Codegen
```python
# computronium/experiment/execution/dashboard/messages.py
from dataclasses import dataclass
from typing import TypedDict

# Single source: Python dataclasses with metadata
@dataclass(frozen=True)
class CampaignMetrics:
    campaign_id: str
    records: list[RecordSummary]
    pareto_flags: list[bool]
    ablation_groups: dict[str, list[RecordSummary]]

# Registry of all message types
WS_MESSAGES = {
    'status_update': StatusData,
    'queue_update': QueueData,
    'campaign_metrics': CampaignMetrics,
    'pipeline_event': PipelineEvent,
}

# Generator: scripts/generate_ws_types.py
def generate_typescript():
    for name, cls in WS_MESSAGES.items():
        # Use dataclass fields → TypeScript interface
        fields = get_dataclass_fields(cls)
        ts = f"export interface {name} {{\n  type: '{name}';\n"
        for field in fields:
            ts += f"  {field.name}: {python_to_ts_type(field.type)};\n"
        ts += "}"
        write_ts(f'src/types/{name}.ts', ts)
    
    # Union type
    union = " | ".join(f"'{k}'" for k in WS_MESSAGES)
    write_ts('src/types/ws-messages.ts', f"export type WSMessageType = {union};")
```

**Benefits**:
- Impossible to have mismatched types
- Adding field in Python → TypeScript error until regenerated
- Documentation auto-generated from docstrings

---

## 7. Campaign Metrics Endpoint: Reuse ReportGenerator

### Current Plan (Duplicate Logic)
```python
# web.py - NEW ENDPOINT DUPLICATES REPORT LOGIC
@app.get("/api/campaigns/{campaign_id}/metrics")
async def api_campaign_metrics(campaign_id: str):
    records = store.query_records(run_id=campaign_id)
    pareto = compute_pareto_flags(records)        # DUPLICATE
    ablation = contrast_groups(records, "credit") # DUPLICATE
    return JSONResponse({...})
```

### Elegant Alternative: Thin Wrapper Around ReportGenerator
```python
# web.py - THIN WRAPPER
from computronium.experiment.surface.report import ReportGenerator

@app.get("/api/campaigns/{campaign_id}/metrics")
async def api_campaign_metrics(campaign_id: str):
    store = RecordStore(StoreConfig(path=Path(config.store_path), read_only=True))
    with store:
        generator = ReportGenerator(store)
        
        # Reuse existing logic
        records = generator._store.query_records(run_id=campaign_id)
        pareto_points, _ = compute_pareto_frontier(records, ["val_acc", "walltime_s"])
        pareto_ids = {p["record_id"] for p in pareto_points}
        
        ablation_html = generator._generate_ablation_html(campaign_id)
        # Parse HTML? Better: expose structured data from ReportGenerator
        
        return JSONResponse({
            "records": [record_to_dict(r) for r in records],
            "pareto": [r.record_id in pareto_ids for r in records],
            "ablation_groups": generator.get_ablation_groups(campaign_id),  # NEW METHOD
        })
```

**Needed in ReportGenerator**:
```python
# Add to ReportGenerator class
def get_ablation_groups(self, run_id: str) -> dict[str, list[dict]]:
    """Return structured ablation groups for API consumption."""
    records = list(self._store.query_records(run_id=run_id))
    groups = {}
    for axis in _ABLATION_AXES:
        for group in contrast_groups(records, axis):
            groups[f"{axis}:{hash(tuple(sorted(group.keys())))}"] = [
                record_to_dict(r) for arm in group.values() for r in arm
            ]
    return groups
```

**Benefits**:
- Zero logic duplication
- ReportGenerator is single source of truth for analysis
- API stays in sync with reports automatically

---

## 8. Record → Dict Conversion: Centralized Serializer

### Current Plan (Scattered)
```python
# Multiple places in web.py
def record_to_dict(r: Record) -> dict:
    return {
        "record_id": r.record_id,
        "coordinate": { "credit": r.credit, ... },
        "payload": r.payload,
        "verdict": r.status.gate_verdict.value,
        # ... repeated in 3+ places
    }
```

### Elegant Alternative: Protocol + Single Implementation
```python
# computronium/experiment/evidence/serializers.py
from typing import Protocol

class RecordSerializer(Protocol):
    def to_api_dict(self, record: Record) -> dict: ...

class DefaultRecordSerializer:
    def to_api_dict(self, record: Record) -> dict:
        return {
            "record_id": record.record_id,
            "cell_key": record.cell_key,
            "coordinate": {
                "substrate": record.substrate,
                "geometry": record.geometry,
                "dynamics": record.dynamics,
                "plasticity": record.plasticity,
                "credit": record.credit,
                "update": record.update,
            },
            "params": record.params,
            "payload": record.payload,
            "schedule": record.schedule.to_dict(),
            "provenance": record.provenance.to_dict(),
            "status": {
                "gate_verdict": record.status.gate_verdict.value,
                "maturity": record.status.maturity.value,
                "quarantine": record.status.quarantine,
            },
            "verification_level": self._verification_level(record),
        }
    
    def _verification_level(self, record: Record) -> str:
        # maturity l1 → VL1, l2 → VL4 (per verification taxonomy)
        return {"l1": "VL1", "l2": "VL4"}.get(record.status.maturity.value, "VL?")

# Singleton
serializer = DefaultRecordSerializer()

# In web.py:
from computronium.experiment.evidence.serializers import serializer
return JSONResponse({"records": [serializer.to_api_dict(r) for r in records]})
```

**Benefits**:
- Single serialization logic
- Swappable for testing (mock serializer)
- Verification level mapping in one place

---

## 9. Three.js Object Pooling (Performance + Elegance)

### Current Plan (Create/Destroy)
```typescript
// src/discovery-map.ts - NAIVE
updateMetrics(metrics) {
  this.cells.forEach(c => this.scene.remove(c.mesh));
  this.cells.clear();
  metrics.records.forEach(r => this.createCellMesh(r)); // NEW meshes every update
}
```

### Elegant Alternative: Object Pool
```typescript
// src/discovery-map.ts - POOLED
class CellPool {
  private pool: Map<string, THREE.Mesh> = new Map();
  private active: Set<string> = new Set();

  getOrCreate(key: string, factory: () => THREE.Mesh): THREE.Mesh {
    let mesh = this.pool.get(key);
    if (!mesh) {
      mesh = factory();
      this.pool.set(key, mesh);
    }
    this.active.add(key);
    return mesh;
  }

  prune() {
    for (const [key, mesh] of this.pool) {
      if (!this.active.has(key)) {
        this.scene.remove(mesh);
        mesh.geometry.dispose();
        mesh.material.dispose();
        this.pool.delete(key);
      }
    }
    this.active.clear();
  }
}

// Usage:
updateMetrics(metrics) {
  const newKeys = new Set(metrics.records.map(r => r.cell_key));
  
  // Update or create
  for (const record of metrics.records) {
    const mesh = this.pool.getOrCreate(record.cell_key, () => this.createCellMesh(record));
    this.updateCellMesh(mesh, record);
  }
  
  // Prune removed
  this.pool.prune();
}
```

**Benefits**:
- 60fps with 1000+ cells (no GC pressure)
- Smooth transitions (mesh reused, just properties updated)
- Clean separation: pool manages lifecycle, component manages visuals

---

## 10. Configuration: DashboardConfig as Typed Registry

### Current Plan (Dataclass)
```python
@dataclass(frozen=True, slots=True)
class DashboardConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    update_interval: float = 2.0
    store_path: str | None = None
    campaign_queue: CampaignQueue | None = None
    enable_websockets: bool = True
    demo_mode: bool = False
    read_only: bool = False
```

### Elegant Alternative: Registry of Config Schemas
```python
# computronium/experiment/execution/dashboard/config.py
from computronium.experiment.schema.registry import Registry

@dataclass(frozen=True, slots=True)
class ConfigSchema:
    name: str
    fields: dict[str, FieldSpec]  # type, default, validator, description

CONFIG_REGISTRY = Registry[ConfigSchema]()

# Register dashboard config schema
CONFIG_REGISTRY.register(ConfigSchema(
    name="dashboard",
    fields={
        "host": FieldSpec(type=str, default="0.0.0.0", description="Bind address"),
        "port": FieldSpec(type=int, default=8080, validator=lambda p: 1024 <= p <= 65535),
        "update_interval": FieldSpec(type=float, default=2.0, validator=lambda i: i > 0),
        "store_path": FieldSpec(type=Path | None, default=None),
        "read_only": FieldSpec(type=bool, default=True, description="Prevents store lock contention"),
    }
))

# Auto-generates:
# - CLI argument parser (from fields)
# - JSON schema for config file validation
# - Documentation (from descriptions)
# - TypeScript config type for frontend
```

**Benefits**:
- CLI, config file, docs, frontend types all from single schema
- Validators declared once, enforced everywhere
- Adding field = one registry entry, auto-propagates

---

## Summary: Elegance Scorecard

| Pattern | Applied In Plan? | Opportunity | Effort |
|---------|------------------|-------------|--------|
| Registry (WebSocket handlers) | ❌ | High — eliminates switch/router boilerplate | Low |
| Registry (Components) | ❌ | High — auto-discovery, lifecycle | Low |
| Registry (Chart types) | ❌ | Medium — Plotter extensibility | Low |
| Registry (Axis metadata) | ❌ | High — leverages existing Python registries | Medium (codegen) |
| Single-source palette | ❌ | High — Python/TS/CSS sync | Low (codegen) |
| WS message codegen | ❌ | High — type safety | Medium (codegen) |
| ReportGenerator reuse | ❌ | High — zero logic duplication | Low (add method) |
| Record serializer | ❌ | Medium — centralize conversion | Low |
| Object pooling | ❌ | Medium — performance + elegance | Low |
| Config registry | ❌ | Low — nice to have | Medium |

---

## Recommended Minimal Elegance Additions (Phase 0)

**Do These in Phase 0** (before writing components):

1. **`scripts/generate_palette.py`** → generates `_palette.py`, `palette.ts`, `palette.css`
2. **`scripts/generate_axis_metadata.py`** → generates `axis-metadata.json` from Python registries
3. **Add `get_ablation_groups()` to `ReportGenerator`** → API reuses report logic
4. **Create `RecordSerializer`** → single serialization point
5. **Define `MessageRouter` + `ComponentRegistry` base classes** → components use from Day 1

**Defer to v2**:
- WebSocket message codegen (manual types OK for v1)
- Config registry (dataclass sufficient)
- Chart type registry (3 charts hardcoded is fine)

---

## Implementation Priority

```
Phase 0 (Day 1):
  ├─ generate_palette.py
  ├─ generate_axis_metadata.py  
  ├─ ReportGenerator.get_ablation_groups()
  ├─ RecordSerializer
  ├─ MessageRouter base class
  └─ ComponentRegistry base class

Phase 1+:
  Components use registries from Day 1 → zero boilerplate additions
```

This gives **maximum elegance for minimum upfront cost** — the registry patterns are established in the codebase, we're just applying them to the new dashboard frontend.