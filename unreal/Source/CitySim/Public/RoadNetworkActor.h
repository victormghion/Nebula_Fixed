#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/SplineComponent.h"
#include "RoadNetworkActor.generated.h"

USTRUCT()
struct FGraphNode
{
	GENERATED_BODY()
	UPROPERTY() int32 Id = -1;
	UPROPERTY() FVector Position = FVector::ZeroVector;
};

USTRUCT()
struct FGraphEdge
{
	GENERATED_BODY()
	UPROPERTY() int32 From = -1;
	UPROPERTY() int32 To = -1;
	UPROPERTY() float LengthM = 0.f;
	UPROPERTY() float SpeedKph = 40.f;
	UPROPERTY() int32 Lanes = 1;
	UPROPERTY() bool bOneway = true;
};

UCLASS(BlueprintType, Blueprintable)
class CITYSIM_API ARoadNetworkActor : public AActor
{
	GENERATED_BODY()

public:
	ARoadNetworkActor();
	virtual void OnConstruction(const FTransform& Transform) override;

	// JSON file with { nodes:[{id,x,y,z}], edges:[{from,to,length_m,speed_kph,lanes,oneway}] }
	UPROPERTY(EditAnywhere, Category="RoadNetwork")
	FFilePath LanesGraphJson;

	// Scale to convert OSM meters to Unreal centimeters (default: 100 cm per 1 m)
	UPROPERTY(EditAnywhere, Category="RoadNetwork")
	float WorldScale = 100.f;

	// Created spline components per edge
	UPROPERTY(VisibleAnywhere, Category="RoadNetwork")
	TArray<TObjectPtr<USplineComponent>> RoadSplines;

	UFUNCTION(BlueprintCallable, Category="RoadNetwork")
	const TArray<USplineComponent*>& GetRoadSplines() const { return RoadSplines; }

private:
	void ClearExisting();
	bool LoadGraph(TArray<FGraphNode>& OutNodes, TArray<FGraphEdge>& OutEdges) const;
	void BuildSplines(const TArray<FGraphNode>& Nodes, const TArray<FGraphEdge>& Edges);
};


