UE5 CitySim Starter
===================

O que vem incluso
-----------------
- `CitySim.uproject`: projeto básico 5.4 com plugins úteis.
- `Source/CitySim`: módulo C++ com `ASpawnManager` que instancia pedestres a partir de um `UDataTable` (CSV importado).
- Tipos/struct `FSpawnPointRow` para DataTable (colunas: X, Y, Z, SpawnTag).

Como abrir e compilar
--------------------
1. Instale Unreal Engine 5.4+.
2. Copie a pasta `unreal/` para um diretório de projetos UE (ou mantenha aqui).
3. Dê duplo clique em `CitySim.uproject`. Se pedir para compilar, aceite.
4. Abra o projeto no Editor; verifique se o módulo `CitySim` aparece na lista de C++.

Criar DataTable a partir do CSV
-------------------------------
1. Exporte `spawn_points.csv` com `tools/osm_export.py` (ou use um CSV próprio).
2. No Editor, `Import` o CSV:
   - RowStruct: `FSpawnPointRow`
   - Salve como `DT_SpawnPoints`.

Usar o Spawner
--------------
1. No nível, adicione um `SpawnManager` (Place Actors).
2. Nas propriedades:
   - `SpawnPointsTable`: selecione `DT_SpawnPoints`.
   - `PedestrianActorClass`: selecione `APedestrianPawn` (ou seu BP/agent MassAI).
   - `MaxSpawnCount`: ajuste conforme performance.
3. Ao iniciar o Play, agentes são instanciados nas posições do DataTable.

MassAI
------
Este starter não inclui configurações complexas de MassAI. Use sua `EntityConfig`/`Processor` preferida e aponte `PedestrianActorClass` para um BP que já possua setup de MassAI.

Próximos passos
---------------
- Adicionar um leitor de `lanes_graph.json` para gerar splines de tráfego.
- Implementar um `VehicleSpawner` e controladores básicos.
- Adicionar Editor Utility Widgets para importar GeoJSON → atores/splines.

Rede viária (splines) e veículos
--------------------------------
- `ARoadNetworkActor`: lê `lanes_graph.json` (campo Nodes/Edges) e cria splines por aresta. Configure:
  - Em detalhes do ator no nível, indique o arquivo em `LanesGraphJson`.
  - Ajuste `WorldScale` (100 = metros para centímetros).
- `AVehicleSpawner`: instancia veículos ao longo das splines. Configure:
  - `RoadNetwork`: referência ao `ARoadNetworkActor` do nível.
  - `VehicleClass`: seu pawn/actor de veículo.
  - `MaxVehicles`: quantidade inicial.

Exemplo rápido:
1. Coloque um `ARoadNetworkActor` no mapa e aponte para `unreal/data/samples/lanes_graph.json`.
2. Coloque um `AVehicleSpawner` e referencie o `ARoadNetworkActor`.
3. Em `VehicleClass`, use `AVehiclePawnSimple` como exemplo.
4. Dê Play: veículos serão instanciados em pontos aleatórios das splines.

Exportador integrado (padrão em unreal/data/generated)
------------------------------------------------------
O script `tools/osm_export.py` agora exporta por padrão para `unreal/data/generated/`:

```bash
python tools/osm_export.py --place "São Caetano do Sul, São Paulo, Brazil"
```

Arquivos gerados:
- `unreal/data/generated/roads.geojson`
- `unreal/data/generated/buildings.geojson`
- `unreal/data/generated/lanes_graph.json`
- `unreal/data/generated/spawn_points.csv`

Importe o CSV como DataTable (RowStruct `FSpawnPointRow`) e selecione o JSON no `ARoadNetworkActor`.


