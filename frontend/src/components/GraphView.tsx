import { memo, useEffect, useMemo, useRef, useState } from "react";
import ForceGraph2D, { ForceGraphMethods } from "react-force-graph-2d";
import { GraphEdge, GraphNode } from "../api";

type GraphViewProps = {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedNodeId?: string | null;
  onNodeSelect: (nodeId: string) => void;
};

const typeColors: Record<string, string> = {
  concept: "#38bdf8",
  condition: "#f97316",
  treatment: "#34d399",
  anatomy: "#a855f7",
  other: "#cbd5f5"
};

const GraphView = ({ nodes, edges, selectedNodeId, onNodeSelect }: GraphViewProps) => {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const fgRef = useRef<ForceGraphMethods | null>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [hoveredLink, setHoveredLink] = useState<GraphEdge | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width, height } = entry.contentRect;
        setDimensions({ width, height });
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const { graphData, nodeMap } = useMemo(() => {
    const map = new Map<string, GraphNode>();
    nodes.forEach((node) => {
      map.set(node.id, node);
    });

    const filteredEdges = edges.filter((edge) => {
      if (!map.has(edge.source) || !map.has(edge.target)) {
        console.warn("Skipping edge with missing node", edge);
        return false;
      }
      return true;
    });

    return {
      nodeMap: map,
      graphData: {
        nodes: nodes.map((node) => ({ ...node, name: node.label })),
        links: filteredEdges.map((edge) => ({ ...edge, source: edge.source, target: edge.target }))
      }
    };
  }, [edges, nodes]);

  const adjacency = useMemo(() => {
    const map = new Map<string, Set<string>>();
    graphData.links.forEach((edge) => {
      const source = String(edge.source);
      const target = String(edge.target);
      if (!map.has(source)) map.set(source, new Set());
      if (!map.has(target)) map.set(target, new Set());
      map.get(source)?.add(target);
      map.get(target)?.add(source);
    });
    return map;
  }, [graphData.links]);

  const highlightedNodes = useMemo(() => {
    const active = selectedNodeId ?? hoveredNode ?? hoveredLink?.source ?? hoveredLink?.target;
    if (!active) return new Set<string>();
    const neighbors = adjacency.get(active) ?? new Set<string>();
    return new Set([active, ...neighbors]);
  }, [adjacency, hoveredLink, hoveredNode, selectedNodeId]);

  const highlightedEdges = useMemo(() => {
    if (hoveredLink) return new Set<string>([hoveredLink.id]);
    const active = selectedNodeId ?? hoveredNode;
    if (!active) return new Set<string>();
    const set = new Set<string>();
    graphData.links.forEach((edge) => {
      const id = (edge as GraphEdge).id;
      if (edge.source === active || edge.target === active) {
        set.add(id);
      }
    });
    return set;
  }, [graphData.links, hoveredLink, hoveredNode, selectedNodeId]);

  useEffect(() => {
    if (!fgRef.current || !selectedNodeId) return;
    const api = fgRef.current as ForceGraphMethods & { graphData?: () => any };

    if (typeof api.centerAt !== "function") {
      return;
    }

    const currentGraph = typeof api.graphData === "function" ? api.graphData() : null;
    const renderedNode = currentGraph?.nodes?.find(
      (node: GraphNode & { x: number; y: number }) => node.id === selectedNodeId
    );

    if (renderedNode && typeof renderedNode.x === "number" && typeof renderedNode.y === "number") {
      api.centerAt(renderedNode.x, renderedNode.y, 600);
      api.zoom(4, 600);
    }
  }, [selectedNodeId]);

  const handleResetView = () => fgRef.current?.zoomToFit(600, 80);

  return (
    <div className="graph-container" ref={containerRef}>
      <div className="graph-overlay">
        <div className="graph-stats">
          <span>{graphData.nodes.length} nodes</span>
          <span>{graphData.links.length} relations</span>
        </div>
        <div className="graph-legend">
          {Object.entries(typeColors).map(([type, color]) => (
            <span key={type}>
              <span className="legend-dot" style={{ backgroundColor: color }} />
              {type}
            </span>
          ))}
        </div>
        <button className="graph-reset" onClick={handleResetView}>
          Reset View
        </button>
      </div>
      <ForceGraph2D
        ref={fgRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={graphData}
        backgroundColor="#0f172a"
        cooldownTicks={80}
        linkHoverPrecision={10}
        nodeRelSize={6}
        onNodeClick={(node) => {
          if (node.id) {
            onNodeSelect(String(node.id));
          }
        }}
        onNodeHover={(node) => setHoveredNode(node?.id ? String(node.id) : null)}
        onLinkHover={(link) => setHoveredLink(link ? (link as GraphEdge) : null)}
        onBackgroundClick={() => {
          setHoveredNode(null);
          setHoveredLink(null);
        }}
        linkColor={(link) => {
          const edge = link as GraphEdge;
          if (hoveredLink?.id === edge.id) return "#facc15";
          return highlightedEdges.has(edge.id) ? "rgba(250, 204, 21, 0.8)" : "rgba(148, 163, 184, 0.25)";
        }}
        linkWidth={(link) => (highlightedEdges.has((link as GraphEdge).id) ? 2.4 : 0.8)}
        linkDirectionalParticles={(link) => (highlightedEdges.has((link as GraphEdge).id) ? 2 : 0)}
        linkDirectionalParticleSpeed={0.006}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const label = String((node as any).label || node.id);
          const color = typeColors[(node as any).type] ?? "#38bdf8";
          const isHighlighted = highlightedNodes.has(String(node.id));
          const fontSize = Math.max(8 / globalScale, 3);

          ctx.save();
          ctx.fillStyle = isHighlighted ? color : `${color}55`;
          ctx.beginPath();
          ctx.arc(node.x ?? 0, node.y ?? 0, isHighlighted ? 6 : 4, 0, 2 * Math.PI, false);
          ctx.fill();

          if (selectedNodeId && node.id === selectedNodeId) {
            ctx.strokeStyle = "#facc15";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(node.x ?? 0, node.y ?? 0, 9, 0, 2 * Math.PI, false);
            ctx.stroke();
          }

          if (isHighlighted) {
            ctx.font = `${fontSize}px Inter`;
            ctx.fillStyle = "#e2e8f0";
            ctx.fillText(label, (node.x ?? 0) + 8, (node.y ?? 0) + 3);
          }

          ctx.restore();
        }}
        linkCanvasObjectMode={() => "after"}
        linkCanvasObject={(link, ctx, globalScale) => {
          const edge = link as GraphEdge;
          if (hoveredLink?.id !== edge.id) return;

          const start = link.source as any;
          const end = link.target as any;
          const middleX = (start.x + end.x) / 2;
          const middleY = (start.y + end.y) / 2;

          const label = `${edge.source} ${edge.relation} ${edge.target}`;
          const fontSize = Math.max(10 / globalScale, 4);

          ctx.save();
          ctx.font = `${fontSize}px Inter`;
          const textWidth = ctx.measureText(label).width;
          const padding = 6;

          ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
          ctx.strokeStyle = "rgba(250, 204, 21, 0.8)";
          ctx.lineWidth = 0.5;
          ctx.beginPath();
          ctx.roundRect(middleX - textWidth / 2 - padding, middleY - fontSize, textWidth + padding * 2, fontSize * 1.8, 6);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = "#facc15";
          ctx.fillText(label, middleX - textWidth / 2, middleY + fontSize * 0.1);
          ctx.restore();
        }}
      />
    </div>
  );
};

export default memo(GraphView);
