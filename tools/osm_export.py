import argparse
import json
import math
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import networkx as nx
import osmnx as ox
import pandas as pd
from shapely.geometry import Point, Polygon, LineString, mapping
from shapely.ops import unary_union


@dataclass
class ExportPaths:
	output_dir: str
	roads_geojson: str
	buildings_geojson: str
	lanes_graph_json: str
	spawn_points_csv: str


def ensure_output_paths(output_dir: str) -> ExportPaths:
	os.makedirs(output_dir, exist_ok=True)
	return ExportPaths(
		output_dir=output_dir,
		roads_geojson=os.path.join(output_dir, "roads.geojson"),
		buildings_geojson=os.path.join(output_dir, "buildings.geojson"),
		lanes_graph_json=os.path.join(output_dir, "lanes_graph.json"),
		spawn_points_csv=os.path.join(output_dir, "spawn_points.csv"),
	)


def load_place_geometry(place: Optional[str], polygon_path: Optional[str]) -> Polygon:
	if polygon_path:
		with open(polygon_path, "r", encoding="utf-8") as f:
			geo = json.load(f)
		shape = ox.geometries.geometries_from_featurecollection(geo)
		geom = unary_union(shape.geometry.values)
		if not isinstance(geom, (Polygon,)):
			geom = geom.convex_hull
		return geom
	if not place:
		raise ValueError("Either --place or --polygon must be provided")
	gdf = ox.geocode_to_gdf(place)
	geom = gdf.iloc[0].geometry
	if not isinstance(geom, (Polygon,)):
		geom = geom.convex_hull
	return geom


def export_roads(geom: Polygon, roads_path: str) -> Tuple[nx.MultiDiGraph, List[LineString]]:
	G = ox.graph_from_polygon(geom, network_type="drive", simplify=True)
	edges_gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)
	edges_gdf.to_file(roads_path, driver="GeoJSON")
	lines = [geom for geom in edges_gdf.geometry if isinstance(geom, LineString)]
	return G, lines


def export_buildings(geom: Polygon, buildings_path: str) -> None:
	tags = {"building": True}
	buildings = ox.geometries_from_polygon(geom, tags)
	# Keep only polygonal footprints
	buildings = buildings[buildings.geometry.type.isin(["Polygon", "MultiPolygon"])]
	if buildings.empty:
		# Create empty valid GeoJSON
		with open(buildings_path, "w", encoding="utf-8") as f:
			json.dump({"type": "FeatureCollection", "features": []}, f)
		return
	buildings.to_file(buildings_path, driver="GeoJSON")


def graph_to_lane_json(G: nx.MultiDiGraph, out_path: str) -> None:
	nodes = []
	edges = []
	node_id_map: Dict[int, int] = {}
	for i, (nid, data) in enumerate(G.nodes(data=True)):
		nodes.append(
			{
				"id": i,
				"x": float(data["x"]),
				"y": float(data["y"]),
				"z": 0.0,
			}
		)
		node_id_map[nid] = i
	for uid, vid, key, data in G.edges(keys=True, data=True):
		length = float(data.get("length", 0.0))
		speed_kph = 40.0
		if "maxspeed" in data:
			try:
				speed_kph = float(str(data["maxspeed"]).split()[0])
			except Exception:
				pass
		lanes = int(data.get("lanes", 1)) if str(data.get("lanes", "1")).isdigit() else 1
		oneway = bool(data.get("oneway", True))
		edges.append(
			{
				"from": node_id_map[uid],
				"to": node_id_map[vid],
				"length_m": length,
				"speed_kph": speed_kph,
				"lanes": lanes,
				"oneway": oneway,
			}
		)
	with open(out_path, "w", encoding="utf-8") as f:
		json.dump({"nodes": nodes, "edges": edges}, f, ensure_ascii=False, indent=2)


def generate_spawn_points(sidewalk_geom: Polygon, road_lines: List[LineString], out_csv: str, count: int) -> None:
	points: List[Tuple[float, float]] = []
	if not road_lines:
		df = pd.DataFrame(columns=["x", "y", "z", "spawn_tag"])
		df.to_csv(out_csv, index=False)
		return
	# Use road midpoints as a simple baseline for spawn locations
	for line in road_lines:
		if line.length <= 1.0:
			continue
		midpoint = line.interpolate(0.5, normalized=True)
		points.append((midpoint.x, midpoint.y))
	# Sample additional random points nearby roads
	random.seed(42)
	while len(points) < count:
		line = random.choice(road_lines)
		t = random.random()
		pt = line.interpolate(t, normalized=True)
		# Small perpendicular jitter
		jitter_len = random.uniform(-2.0, 2.0)
		points.append((pt.x + jitter_len, pt.y))
	rows = [{"x": x, "y": y, "z": 0.0, "spawn_tag": "pedestrian"} for x, y in points[:count]]
	pd.DataFrame(rows).to_csv(out_csv, index=False)


def main() -> None:
	parser = argparse.ArgumentParser(description="Export OSM data for Unreal ingestion (roads, buildings, lane graph, spawn points).")
	group = parser.add_mutually_exclusive_group(required=False)
	group.add_argument("--place", type=str, default="São Caetano do Sul, São Paulo, Brazil", help="Place name to geocode and export")
	group.add_argument("--polygon", type=str, help="Path to a GeoJSON polygon FeatureCollection as AOI")
	parser.add_argument("--output", type=str, default=os.path.join(\"unreal\", \"data\", \"generated\"), help="Output directory (default: unreal/data/generated)")
	parser.add_argument("--spawn-count", type=int, default=500, help="Approximate number of pedestrian spawn points")
	args = parser.parse_args()

	paths = ensure_output_paths(args.output)
	print(f"[OSM] Resolving geometry for {args.place or args.polygon}")
	geom = load_place_geometry(args.place, args.polygon)

	print("[OSM] Exporting roads...")
	G, road_lines = export_roads(geom, paths.roads_geojson)
	print(f"[OK] Roads -> {paths.roads_geojson}")

	print("[OSM] Exporting buildings...")
	export_buildings(geom, paths.buildings_geojson)
	print(f"[OK] Buildings -> {paths.buildings_geojson}")

	print("[OSM] Building lane graph...")
	graph_to_lane_json(G, paths.lanes_graph_json)
	print(f"[OK] Lane graph -> {paths.lanes_graph_json}")

	print("[OSM] Generating spawn points...")
	generate_spawn_points(geom, road_lines, paths.spawn_points_csv, args.spawn_count)
	print(f"[OK] Spawn points -> {paths.spawn_points_csv}")

	print(f"[DONE] Export complete in {paths.output_dir}")


if __name__ == "__main__":
	main()


