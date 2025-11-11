Unreal Engine 5 Data Pipeline (São Caetano do Sul)
==================================================

Visão geral
-----------
Este diretório contém um exportador OSM para gerar dados iniciais do mapa de São Caetano do Sul para ingestão no Unreal Engine 5 (World Partition/PCG/Houdini/MassAI).

Saídas geradas
--------------
- unreal_export/roads.geojson: malha viária simplificada (drive).
- unreal_export/buildings.geojson: footprints dos edifícios.
- unreal_export/lanes_graph.json: grafo de tráfego (nós/arestas, comprimento, velocidade, faixas).
- unreal_export/spawn_points.csv: pontos de spawn para pedestres (MassAI/DataTable).

Pré-requisitos
--------------
- Python 3.10+
- Instalar dependências:

```bash
pip install -r requirements.txt
```

Como exportar São Caetano do Sul
--------------------------------
Exemplo básico (usa geocodificação do lugar):

```bash
python tools/osm_export.py --place "São Caetano do Sul, São Paulo, Brazil" --spawn-count 800
```

Usando um polígono AOI custom (GeoJSON FeatureCollection):

```bash
python tools/osm_export.py --polygon aoi_scs.geojson
```

Importando no UE5 (sugestão)
----------------------------
1. Projeto
   - Habilite World Partition; crie um nível vazio (latlong em centímetros não é crítico nesta fase de PoC).
   - Configure Substrate, Nanite, Lumen.

2. Estradas e prédios
   - Opção A: Houdini Engine ou Procedural Content Generation (PCG) para ler GeoJSON e gerar splines/instâncias.
   - Opção B: Converter GeoJSON para CSV/JSON no formato esperado por um Blueprint/Editor Utility Widget.
   - Aplique HLOD/instancing; use materiais regionais (decal para desgaste/sujeira).

3. Tráfego
   - Converta `lanes_graph.json` em um GraphAsset (código C++/BP) contendo nós/arestas/atributos.
   - Gere `splines` por aresta e AIControllers para veículos com planner simples (custo por comprimento, semáforo).

4. MassAI (pedestres)
   - Importe `spawn_points.csv` como DataTable (RowName opcional; colunas: X, Y, Z, SpawnTag).
   - Crie um Spawner que lê a tabela e instancia agentes MassAI com LOD de lógica por distância.

Perf e orçamentos
-----------------
- Use HLOD agressivo, Virtual Shadow Maps e instanciamento.
- Para lógica: Tick Rate escalonado, State LOD e desativação por oclusão/distância.
- Otimize leitura de arquivos e cache de assets (DDC).

Limitações conhecidas
---------------------
- `buildings.geojson` contém apenas footprints; geração de volumetria é responsabilidade do pipeline (Houdini/PCG).
- `lanes_graph.json` é um grafo simplificado; para comportamento realista, enriqueça com semáforos, preferências, largura de faixa, sentidos por faixa e prioridades.

Próximos passos
---------------
- Adicionar export de calçadas/ciclovias e faixas por sentido.
- Exportar POIs (parques, escolas, comércio) para geração de rotinas de NPCs.
- Ferramentas de visualização in-editor (heatmaps de tráfego/spawns).


